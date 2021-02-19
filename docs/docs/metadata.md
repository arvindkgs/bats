---
id: doc2
title: Metadata
---

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