---
id: doc6
title: Usage
---

On Python => 2.7 run
    `python -m bats`
    
On Python <2.7 (POD it is 2.6) run `python -m bats.__main__`

There are four actions supported:

    Metadata : Reads a metadata.json file that contains the configuration of tests to execute
    Compare : Compares two files that are provided as command-line arguments
    Extract : Extracts a property from a file

## Params:

Pass metadata.json

    $ python -m bats metadata metadata.json

Pass dynamic values - Pass dynamic values that will be replaced in the metadata.json.
    For example if I execute below command,

    $ python -m bats metadata metadata.json -D key=value

Then, it will replace ${key} with 'value' in below metadata.json

    {
    	"name": "Demonstrate dynamic value"
    	"tests": [
    		{
    			"name": "Sample test",
    			"checks": [
    				{
    					"name": "Sample check",
    					"source": {
    						"property": "${key}"
    						"type": "..."
    						"file": "..."
    					}
    					"target": {
    						"property": "${key}"
    						"type": "..."
    						"file": "..."
    					}
    				}
    			]
    		}
    	]
    }

Fail on errors

    $ python -m bats metadata metadata.json --failon MISSING_PROPERTY
