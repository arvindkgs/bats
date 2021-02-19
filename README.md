
# BATS

TL;DR
### BATS is a generic tool that automates your cloud operations validation. BATS provides a simplistic and intuitive interface to define your operation validation tests and automate it. For more information on installation, usage, architecture check [Wiki](https://arvindkgs.com/bats)

Cloud Operations is the umbrella term for all the activities required to make an application run on the cloud and make it available for its customer. 
People in cloud operations perform tasks like - scale out, scale in, update, clone etc.

These tasks update configuration in resources like properties, json, xml files, run shell commands to update OS environment settings, call REST APIs. 

These tasks needs to be validated. This validation activities are time consuming, repetitive, and prone to manual error. These validation are repeated across teams and across verticals and across companies. 
This begs the question, can it be automated? Yes! Using Bats
Bats can be integrated into your CI/CD pipeline and can create reports on success or failure.

It takes an input 'metadata' json passed to it as a command-line argument.

