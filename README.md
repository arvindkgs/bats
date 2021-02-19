# BATS
To validate whether all the configuration files and properties and VM arguments where updated successfully. The series of steps mentioned here needs to be performed to validate that the script completed successfully. Manual checking can lead to misses. This is where the tool can be used to do all the checks to verify the success of Resizing.

It takes an input 'metadata' json passed to it as a command-line argument.

# Flowchart

![Flowchart](Validation%20Suite.png)

# metadata
The main component of the automation tool is metadata. Metadata can be created based on custom requirement. Structure of metadata is as follows:

{

    "name": "Name of validation",

    "log": "location",

    "description": "Description",

    "test": [

        {

            "name": "Test Name",

            "dynamic": [

                        {

                            Resource

                        }

            ]

            "check": [

                {

                    "name": "Check Name",

                    "cardinality": ""

                    "source": {

                        Resource

                    }

                    "target": {

                        Resource

                    }

                }

            ]

        }

    ]

}

check cardinality

    one-to-one (default) : first source item is compared to first target item, second source item to second target item. And so on.
    one-to-many : each source item is compared to all target item

Here one resource item is values from one file.
Resource

{

    "property": "",

    "type": "",

    "key": "Key Name",

    "file": "File path",

    "hostname": "",

    "username": "",

    "password": "",

    "format": "",

    "cardinality": ""

}

    property 

This defines the property to fetch. This is specified for following types as,

JSON - JSONPath. To verify use - https://jsonpath.curiousconcept.com/

XML - XPath

PROPERTIES - Key match

CONF - XPath. (The conf file is converted to an intermediate xml file.)

    type

JSON, XML, PROPERTIES, CONFIG, SHELL, STATIC

If type is JSON, XML, CONFIG, file is required.

    hostname, username, password

used to specific remote file which is fetched using scp

    format

extract data from string using below format

meta-chars: {}, ?

Example:

Format='-Xms{}?'

String='-Xms512m -Xmx8192m -Xss102400k'

Extracted Data=512

    cardinality 

one-to-many= This is default. Consider property is an array. And file is also array. Each property is fetched from all the files.

one-to-one = Consider property is an array. And file is also array. Now first property is fetched from first file, second property from second file. And so on.

Extrapolate


Extrapolation is where values from dynamic map replace the placeholder in the string. The specific value from dynamic map is referred using its key name in the format - ${key}

Example: in string 'wlscluster[${clusterIndex}]' ${clusterIndex}' is replaced by value found for 'clusterIndex' key in dynamic properties

If clusterIndex = [0, 1, 2] then

Result

    wlscluster[0]
    wlscluster[1]
    wlscluster[2]

Hence here one property - 'wlscluster[${clusterIndex}]' results in 3 results.

This can go to multiple levels.

Example:

wlscluster[${clusterIndex}].${clusterName}

clusterIndex = [0, 1, 2] and clusterValue = [a, b, c]

Intermediate Result

    wlscluster[0].${clusterName}
    wlscluster[1].${clusterName}
    wlscluster[2].${clusterName}

Final Result

    wlscluster[0].a
    wlscluster[0].b
    wlscluster[0].c
    wlscluster[1].a
    wlscluster[1].b
    wlscluster[1].c
    wlscluster[2].a
    wlscluster[2].b
    wlscluster[2].c

Here one property wlscluster[${clusterIndex}].${clusterName}  resulted in 3x3 = 9 results. Hence the name extrapolation.

Except type, format, cardinality, key all other resource attributes are extrapolatable

## Build

To build an artifact, cd into the root directory and run `sh build.sh`

This creates in root
```
(ROOT)
|- bats.tar.gz (This is file that should be transferred to the POD/vm where *bats* should run)
|- dist
   |- basic_acceptance_test_suite-0.0.1-py2-none-any.whl
   |- basic-acceptance-test-suite-0.0.1.tar.gz (Package that can be installed directly using pip (pip install ...), or  extracting and running python setup.py install)
   |- README.md
```
   
## Install

    To install on POD, transfer bats.tar.gz
    Expand the archive
    Install running `sh setup.sh`.


## Distribute

If you want to distribute without needing to install on POD, then PyInstaller can be looked into.

NOTE:

    PyInstaller creates OS and python dependent redistributions, so for POD, you may need to have to install PyInstaller on it, transfer the automation-validation-tool source code, run it and get a redistribution.
    I tried unsuccessfuly on POD. (However on my laptop it worked). Command I ran.
        pyinstaller --add-data templates:templates -p automation-validation-tool/dependencies --distpath automation-validation-tool/artifact -n bats __main__.py
        This gives a reditribute called bats in automation-validation-tool/artifact folder
## Folder Structure
```
.
├── build.sh
├── dependencies
│   ├── apacheconfig-0.2.8.tar.gz
│   ├── argparse-1.4.0.tar.gz
│   ├── basic-acceptance-test-suite-0.0.1.tar.gz
│   ├── decorator-4.4.0.tar.gz
│   ├── jsonpath-rw-1.4.0.tar.gz
│   ├── jsonpath-rw-ext-1.2.0.tar.gz
│   ├── pbr-5.2.0.tar.gz
│   ├── ply-3.11.tar.gz
│   └── six-1.12.0.tar.gz
├── Enhancements.txt
├── MANIFEST.in (Resource to be added to python module) 
├── metadatas
│   ├── fa_host
│   ├── ohs-shell-dynamic
│   ├── resizing
│   └── tests
├── README.md
├── scripts
│   ├── runSCPCommand.sh (Test scp command)
│   ├── runSSHCommand.sh (Test ssh command)
│   ├── runTests.sh (Call this after any code modifications, to run unit tests)
│   └── setup.sh (Call this for installing in local vm/laptop, when using virtual environment pass 'dev' argument)
├── setup.py (Install script for artifact, that is bundled with artifact)
├── src
│   └── bats
├── struct
├── tmp
│   ├── dependencies
│   ├── README.md
│   └── setup.sh
└── Validation\ Suite.png (Flow diagram)

```

## Usage
On Python => 2.7 run
    `python -m bats`
    
On Python <2.7 (POD it is 2.6) run `python -m bats.__main__`

There are four actions supported:

    Metadata : Reads a metadata.json file that contains the configuration of tests to execute
    Compare : Compares two files that are provided as command-line arguments
    Extract : Extracts a property from a file
    
Output

   * Script returns 0 on success, 1 on failure.
   * On std-out it only lists failing checks. However log file has details of all the success and failures and errors.
   * By default it does not fail on errors (like FILE_NOT_FOUND, MISSING_PROPERTY). However this can be changed by setting --failon argument
   * Script does not stop on error, or failure, it moves to next test/check

```
Log format is as follows, (for default cardinality: one-to-one)
Log Message Type (Info, Error)	Test Name	Check Name	        Compare Type	Pass / Failed and detailed compare information
INFO	Elastic Search Test	Elastic Search 'NUMBER_OF_NODES' check	COMPARE	        PASSED : $.topology.vmHosts[?(@.hostType=opt1)].elasticSearchNodes([1]) == NUMBER_OF_NODES([u'1'])
INFO	Elastic Search Test	Elastic Search 'ES_HEAP_VALUE' check	COMPARE	        FAILED : $.topology.vmHosts[?(@.hostType=opt1)].['max.heap']([u'6048']) != ES_HEAP_VALUE([u'1536'])
ERROR	JVM Args Test	XX:NewRatio Check	MISSING_PROPERTY	COMPARE         No property: $..wlsClusters[?(@.clusterName=SingletonCluster)].'XX:NewRatio'
```
    
Example log:

```
[[INFO] [Elastic Search Test]   [Elastic Search 'NUMBER_OF_NODES' check]        [COMPARE]]      PASSED : $.topology.vmHosts[?(@.hostType=opt1)].elasticSearchNodes([1]) == NUMBER_OF_NODES([u'1'])
[[INFO] [Elastic Search Test]   [Elastic Search 'ES_HEAP_VALUE' check]  [COMPARE]]      FAILED : $.topology.vmHosts[?(@.hostType=opt1)].['max.heap']([u'6048']) != ES_HEAP_VALUE([u'1536'])
[[ERROR]        [JVM Args Test] [XX:NewRatio Check]     [MISSING_PROPERTY]      [metadatas/tests/jvm/source.json]]      No property: $..wlsClusters[?(@.clusterName=SingletonCluster)].'XX:NewRatio'
```
However, if the check type has 'one-to-many' cardinality in case of multiple files

```
Log Message Type	Test Name	Check Name	Cardinality	File Name	Compare Type	Pass / Failed and detailed compare information
INFO	JVM Args Test	Xms Check	one-to-many	./metadatas/tests/one-to-many/vm1//target.properties	COMPARE	PASSED : $..wlsClusters[?(@.clusterName=UICluster)].Xms([2014]) == fusion.FADomain.UICluster.default.minmaxmemory.main([u'2014'])
```
Example log:

```
[INFO] [JVM Args Test] [Xms Check]     [one-to-many]   [./metadatas/tests/one-to-many/vm1//target.properties]  [COMPARE]]      PASSED : $..wlsClusters[?(@.clusterName=UICluster)].Xms([2014]) == fusion.FADomain.UICluster.default.minmaxmemory.main([u'2014'])
```

### Metadata
Usages:

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
    

