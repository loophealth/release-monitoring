from tqdm import tqdm
import enum
import time
import tempfile
from typing import List, Optional
from uuid import UUID

from sqlalchemy.types import Uuid
from git import RemoteProgress, Repo
from git.exc import GitCommandError
from sqlalchemy import Column, desc, select
from datetime import date, datetime
from github import Github
from github import Auth, Repository

from models import SessionLocal, engine, Base
from models.release import Releases
from models.release import ReleaseActions
from models.release import DeploymentStatus, ReleaseActionApprovals, ReleaseStates
from models.release import Environments
from models.release import ReleaseComments


Base.metadata.create_all(bind=engine)


ACTUALLLY_CREATE_TAGS = False
ACTUALLY_RUN_ACTIONS = False

username = "vinaygb-loop"
# password = "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"
password = "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"


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GithubHelper:
    github = None
    repo: Repository.Repository
    raw_repo: Repo
    REPO_CLONE_PATH_LOCAL: str
    remote: str
    workflow_file: str

    def __init__(self, org: str, repo: str, workflow_file: str):
        self._setup_remote_git(org, repo)
        self.remote = f"https://{username}:{password}@github.com/{org}/{repo}.git"
        self._setup_local_git()
        self.workflow_file = workflow_file

    def _setup_remote_git(self, org: str, repo: str):
        auth = Auth.Token(password)
        github = Github(auth=auth)
        g_org = github.get_organization(org)
        self.repo = g_org.get_repo(repo)

    def _setup_local_git(self):

        self.REPO_CLONE_PATH_LOCAL = tempfile.TemporaryDirectory().name
        st = time.time()
        Repo.clone_from(self.remote, self.REPO_CLONE_PATH_LOCAL,
                        progress=CloneProgress())
        print(f"Cloned in {time.time()-st}s")
        self.raw_repo = Repo(self.REPO_CLONE_PATH_LOCAL)

    def create_tag(self, branch: str, tag_name: str, commit: str | None = None):
        gbranch = self.repo.get_branch(branch)
        head_commit = f"{str(gbranch.commit.sha)}"
        # TODO: Accept a message as well
        print(tag_name)
        tag = self.repo.create_git_tag(
            tag_name, f"Release tag created out of main on {datetime.now()}", head_commit, type="commit")
        if ACTUALLLY_CREATE_TAGS:
            self.repo.create_git_ref(f"refs/tags/{tag.tag}", tag.sha)
        return tag

    @staticmethod
    def parse_environment(env: Environments) -> str:
        match env:
            case Environments.dev:
                return 'DEV'
            case Environments.qa:
                return 'QA'
            case Environments.production:
                return 'PROD'
            case Environments.beta:
                return 'BETA'
            case _:
                raise Exception('NKN enro')

    def run_github_deployment_action(self, workflow: str, tag: str, env: Environments):
        wflow = self.repo.get_workflow(workflow)
        env_str = self.parse_environment(env)
        if ACTUALLY_RUN_ACTIONS:
            wflow.create_dispatch(tag, {
                'deploy_env': env_str
            })
            print(
                f"Deployment triggered with {tag} for {env} , state as of now is {wflow.state}")
        return wflow

    def cherry_pick_and_push(self, base_tag: str, commits: List[str], target_tag: str) -> None | Exception:
        try:

            if ACTUALLLY_CREATE_TAGS:
                self.raw_repo.git.checkout(base_tag)
                for commit in commits:
                    self.raw_repo.git.cherry_pick(commit)
                tag = self.raw_repo.create_tag(
                    target_tag, message=f'Upgrading {base_tag} to {target_tag} with {len(commits)} commits')
                self.raw_repo.remotes.origin.push(tag, force=True)
        except GitCommandError as e:
            return e


class ReleaseManager:
    db = SessionLocal()
    ghelper: GithubHelper
    workflow_file: str

    def __init__(self, org: str, repo: str, workflow_file: str):
        self.org = org
        self.repo = repo
        self.ghelper = GithubHelper(org, repo, workflow_file)
        self.workflow_file = workflow_file

    def _get_highest_version(self):
        stmt = select(ReleaseActions).order_by(desc(ReleaseActions.created_on))
        latest_action = self.db.execute(stmt).scalars().first()
        if latest_action:
            return latest_action.version

        return "1.0.0"

    def _get_release_env(self):
        stmt = select(ReleaseActions).order_by(desc(ReleaseActions.version))
        latest_action = self.db.execute(stmt).scalars().first()
        return latest_action.version if latest_action else None

    def _get_current_version(self):
        highest_version = self._get_highest_version()

        return str(highest_version)

    def _get_next_version(self):
        highest_version = self._get_highest_version()
        version_parts = highest_version.split('.')
        major, minor, dev = map(int, version_parts)
        minor += 1
        return f"{major}.{minor}.0"

    def _get_next_fix_version(self):
        highest_version = self._get_highest_version()

        if highest_version is None:
            raise Exception('Trying to create an action without a release!')
        print(
            f"While finding next fix, highest version now is {highest_version}")
        version_parts = highest_version.split('.')
        major, minor, dev = map(int, version_parts)
        dev += 1
        return f"{major}.{minor}.{dev}"

    @staticmethod
    def get_tag_name_from_version(version: str):
        return f"LB-v{version}"

    def create_release(self, branch: str, release_name: str):
        """
            Following steps need to happen inside a release creation:
            1. Creates a release entry with meta, default status, and default env.
            2. Create a version for the release and mark the number as v1 (default 0 and 1-index verbiage).
            3. Creates a tag releases/<release_name>/v<version> out of the specified branch "HEAD" and pushes it.
            4. Updates the release status to ready_for_release.
        """
        with self.db.begin():
            release = Releases(name=f"RM_RELEASES/{release_name}")
            self.db.add(release)
            self.db.flush()

            version = self._get_next_version()
            tag_name = self.get_tag_name_from_version(version)
            tag = self.ghelper.create_tag(
                branch, tag_name)
            wflow = self.ghelper.run_github_deployment_action(
                self.workflow_file, tag.tag, Environments.dev)
            action = ReleaseActions(
                release_id=release.id,
                comment="Deploying release",
                version=version,
                action_url=f"https://github.com/{self.org}/{self.repo}/actions/{tag_name}",
                tag_url=f"https://github.com/{self.org}/{self.repo}/releases/tag/{tag_name}",
                deployment_status='running'
            )
            self.db.add(action)
            self.db.flush()
            return release

    def list_releases(self):
        stmt = select(Releases)
        for release in self.db.execute(stmt).scalars():
            print(release)

    def hotfix(self, release_id: int, commits: List[str]):
        with self.db.begin():
            print(f"Hotfixing {release_id} with ${commits}")
            release = self.db.query(ReleaseActions).where(
                ReleaseActions.release_id == release_id).order_by(ReleaseActions.created_on).first()
            if release is not None:

                print(release)
                current_version = self._get_current_version()
                version = self._get_next_fix_version()
                tag_name = self.get_tag_name_from_version(version)
                current_tag = self.get_tag_name_from_version(current_version)
                print(
                    f"Creating a new tag on top of the release head, {tag_name} {version}")
                err = self.ghelper.cherry_pick_and_push(
                    current_tag, commits, tag_name)
                if isinstance(err, Exception):
                    print("Failed to create a tag something went wrong", err)
                    return err

                action = ReleaseActions(
                    release_id=release_id,
                    comment=f"Deploying v${version} as hotfix on top of v${current_version}",
                    version=version,
                    action_url=f"https://github.com/{self.org}/{self.repo}/actions/{tag_name}",
                    tag_url=f"https://github.com/{self.org}/{self.repo}/releases/tag/{tag_name}",
                    deployment_status='running'
                )
                self.ghelper.run_github_deployment_action(
                    self.workflow_file, tag_name, str(action.env))

                print(f"Deploying the tag ${tag_name} to {action.env}")
                self.db.add(action)
                self.db.flush()
                return
            raise Exception("Nkn correct release id kodo dengtini illa andre")

    def approve_release(self, release_id: int, user: str):
        with self.db.begin():
            approval = ReleaseActionApprovals(
                release_action_id=self.get_latest_action_id(release_id),
                approved_by=user,
                approved=True
            )
            self.db.add(approval)
            self.db.flush()

            # Check if there are 2 approvals
            approvals = self.db.query(ReleaseActionApprovals).filter_by(
                release_action_id=approval.release_action_id, approved=True).count()
            if approvals >= 2:
                print("More than 2 approvals found for release, promoting!")
                self.promote_release(release_id)

    def promote_release(self, release_id: int):
        release = self.db.query(Releases).filter_by(id=release_id).first()
        if release is None:
            raise ValueError("Invalid release_id")
        print(release.state)
        next_state = self.get_next_state(release.state)
        if next_state is None:
            raise ValueError("No further state to promote to")

        release.state = next_state
        self.db.commit()
        self.db.flush()

        if next_state in [ReleaseStates.ready_for_release, ReleaseStates.released]:
            # Deploy to the next environment
            self.deploy_release(release_id)

    def get_next_state(self, current_state: ReleaseStates) -> Optional[ReleaseStates]:
        state_order = [
            ReleaseStates.testing,
            ReleaseStates.ready_for_testing,
            ReleaseStates.tested,
            ReleaseStates.ready_for_release,
            ReleaseStates.released,
            ReleaseStates.stable
        ]
        try:
            current_index = state_order.index(current_state)
            return state_order[current_index + 1] if current_index < len(state_order) - 1 else None
        except ValueError:
            return None

    def block_release(self, release_id: int):
        with self.db.begin():
            release = self.db.query(Releases).filter_by(id=release_id).first()
            if release is None:
                raise ValueError("Invalid release_id")

            release.state = ReleaseStates.blocked
            self.db.flush()

    def comment_on_release(self, release_action_id: str, comment: str, user: str):
        with self.db.begin():
            action = self.db.query(ReleaseActions).filter_by(
                id=release_action_id).first()
            if action is None:
                raise ValueError("Invalid release_action_id")

            # Assuming there's a Comment model or similar to store comments
            comment = ReleaseComments(
                release_action_id=release_action_id,
                comment=comment,
                commented_by=user
            )
            self.db.add(comment)
            self.db.flush()

    def mark_release_tested(self, release_id: int):
        with self.db.begin():
            release = self.db.query(Releases).filter_by(id=release_id).first()
            if release is None:
                raise ValueError("Invalid release_id")

            release.state = ReleaseStates.tested
            self.db.flush()

    def deploy_release(self, release_id: int):
        with self.db.begin():
            release = self.db.query(Releases).filter_by(id=release_id).first()
            if release is None:
                raise ValueError("Invalid release_id")

            latest_action = self.db.query(ReleaseActions).filter_by(
                release_id=release_id).order_by(ReleaseActions.created_on.desc()).first()
            if latest_action is None:
                raise ValueError("No actions found for release_id")

            next_env = self.get_next_environment(latest_action.env)
            if next_env is None:
                raise ValueError("No further environment to deploy to")

            version = self._get_next_version()  # Assuming a method to get the next version
            # Assuming a method to get the tag name
            tag_name = self.get_tag_name_from_version(version)

            new_action = ReleaseActions(
                release_id=release_id,
                env=next_env,
                comment="Promoting release",
                version=version,
                action_url=f"https://github.com/{self.org}/{self.repo}/actions/{tag_name}",
                tag_url=f"https://github.com/{self.org}/{self.repo}/releases/tag/{tag_name}",
                deployment_status=DeploymentStatus.running
            )
            self.db.add(new_action)
            self.db.flush()

            # Deploy to the next environment
            self.ghelper.run_github_deployment_action(
                self.workflow_file, new_action.tag_url, next_env)

    def get_latest_action_id(self, release_id: int) -> Column[UUID]:
        latest_action = self.db.query(ReleaseActions).filter_by(
            release_id=release_id).order_by(ReleaseActions.created_on.desc()).first()
        if latest_action is None:
            raise ValueError("No actions found for release_id")
        return latest_action.id

    def get_next_environment(self, current_env: Environments) -> Optional[Environments]:
        env_order: list[Environments] = [
            Environments.dev, Environments.qa,
            Environments.beta, Environments.production]
        try:
            current_index = env_order.index(current_env)
            return env_order[current_index + 1] if current_index < len(env_order) - 1 else None
        except ValueError:
            return None

    def get_release(self, release_id: int) -> Releases:
        release = self.db.query(Releases).filter_by(id=release_id).first()
        if release is None:
            raise ValueError("Invalid release_id")
        return release

    def list_releases(self) -> List[Releases]:
        return self.db.query(Releases).all()

    def get_release_actions(self, release_id: int) -> List[ReleaseActions]:
        return self.db.query(ReleaseActions).filter_by(release_id=release_id).all()

    def get_release_comments(self, release_action_id: UUID) -> List[ReleaseComments]:
        return self.db.query(ReleaseComments).filter_by(release_action_id=release_action_id).all()

    def get_approvals(self, release_id: int) -> List[ReleaseActionApprovals]:
        latest_action_id = self.get_latest_action_id(release_id)
        return self.db.query(ReleaseActionApprovals).filter_by(release_action_id=latest_action_id).all()


class WorkflowRunHook:
    def __init__(self, reponame: str):
        self.reponame = reponame

    def get_workflow_runs(self,):
        raise NotImplementedError


# rm = ReleaseManager("loophealth", "loop-backend", "deploy_backend.yml")
# rm.create_release("main", "weekly_release_1st_june")
# rm.hotfix(1, ["b9277aba8cc720de4b8c08be672d51176843396f"])
# rm.mark_release_tested(1)
# rm.promote_release(1)
# rm.block_release(1)
