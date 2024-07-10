# Release monitoring tool pitch


## What's the current release process?
- An engineer is notified to create a tag out of main
    - tag gets created with unpredictable naming conventions depending on the eng
- The tag gets deployed to QA
- QA does testing 
    - If no bugs approved, go for beta, do sanity then go for prod
    - If bugs, then track them on JIRA, notify the developers and each of the engineers has their own hotfix done
        - If there are parallel hotfixes going then tag names start getting weirder and weirder
- Weekly release is the plan but it never happens within a week


## What's the problem?

- We cannot ship fast if we our literal pipeline to "release" is just undefined with every eng following their own conventions

- We do not maintain versioning on any of our releases, leaving no differences between a major release, a minor release and a hotfix!
- Since multiple teams collaborate to ship a single binary, we need to keep a track of what was shipped
    - This is not the product release notes, instead a changelog which records what changes went in the release
- Super tight dependency on the eng to keep the release cycle, co-ordination required between the team is insane and there's plenty room for mistakes
    - As of today everything is manual, right from creating a tag, deploying it to the env
    - Multiple such incidents where there has been a miscommunication and wrong tags have been deployed to the wrong env


## What are our options?
- As of today I could not find a pre-built solution which we can just straight up adopt in our release process

- A small web app where we can track our releases with the following "tracking" capabilities
    - Web is not a must , APIs we need then we can even make this into a slack bot if we need

- We need a short 2-3 days worth of exploration if we can leverage any pre-existing tool to fit in our needs and processes
    - Even if we choose to build it still need to check with QA and engineers to get to an alignment

### What's included?
- Creating releases ( involves creating tags with the right naming conventions and deploying them to the right env )
- Applying hotfixes on releases and tracking them on the right env
- Automatic versioning which keeps a track of previous release, recognizes minor changes vs a hotfix and maintains the versions accordingly
- Recording a QA go/no-go on a release, any comments related to stability / bugs etc can be tracked

### What's out ?
- Tracking any schema changes in the deployment
- Generating release notes across releases


## How much will this cost?
-  We need 2 weeks of engineering bandwidth , no product / design required since its an internal eng tool

## What will this add?
- It will save us a bunch of engineering time creating tags, deploying them etc
- Stability on our release pipeline will let us focus on the actual engineering
