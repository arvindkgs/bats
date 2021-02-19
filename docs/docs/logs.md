---
id: doc7
title: Logs
---

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
