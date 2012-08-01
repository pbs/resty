Getting started tutorial
============================================================

This tutorial aims to get you started with :mod:`resty` as quickly as possible.

It is made up of a number of examples of increasing complexity, each of which shows one or more useful :mod:`resty` features.

If you have any comments about these tutorials, or suggestions for things we should cover in them, then please contact us via `Github <https://github.com/pbs/resty/>`_


Step 1: Configure the client
----------------------------

:mod:`resty` provides two types of clients:

* the default :mod:`client` - uses summaries if available therefore the interactions with the api are much faster

* :mod:`dumb_client` - does not use summaries and relies strictly on links


.. Note::

    The summary is composed from all additional attributes (not required) that a minimum document representation has. The minimum documentation representation is used whenever a document has a relationship to another document.


Step 2: Load the entrypoint and select a service
------------------------------------------------

The URL where the Service document is located is named the API Entrypoint.
In the provided example we used http://services.pbs.org/ url as an entrypoint and selected the zipcodes service from the available services.

::

    >>> from resty import client
    >>> c = client.load("http://services.pbs.org/")
    >>> c
    <resty.types.Service object at 0x26abd10>

    >>> zipcode_collection = c.service("zipcodes")
    <resty.types.Collection object at 0x2597e90>


.. Note::

    The call to :mod:`c.service("zicpodes")` will select the top level collection named :mod:`zicpodes`


Step 3: Use filters
-------------------

The :mod:`filters` are used to describe complex interactions that usually require some sort of human input. One particularly common situation is searching trough the elements of a collection. Templates are available only in collections. Since :mod:`zipcode_service` returns a collection we can filter it based on zip.

::

    >>> filtered_zipcodes = zipcode_service.filter('zip', zipcode='22202')


.. Note::

    The :mod:`filter` method takes one positional argument that represents the filter name and a number of keyword arguments where the keys represent the placeholder names and the desired values.


Step 4: Iterating through items
-------------------------------

Items represents the list of objects available in that collection. In the above example the :mod:`filtered_zipcodes` returns a collection with a single object. Let's select the first object from the list:

::

    >>> zipcode_resource = filtered_zipcodes.items()[0]
    >>> zipcode_resource
    <resty.types.Resource object at 0x259fc50>


Step 5: Accessing metadata and usefull content
----------------------------------------------

At this point we have a :mod:`zipcode_resource` and we can extract informations like metadata and content specific informations

::

    >>> print zipcode_resource.content.zipcode
    u'22202'
    >>> print zipcode_resource.class_
    u'Zipcode'



.. Note::

    All properties which are prefixed with $ are considered metadata


Step 6: Using links to interact with available relationships
------------------------------------------------------------

Using the :mod:`related` method one can get from a document to a related document by specifying the relationship name.

Let's see all the callsigns that are available for zipcode 22202 with their corresponding confidence:

::

    >>> callsign_collection = zipcode_resource.related('search')
    >>> for c in callsign_collection.items():
    >>>     print c.related('related').content.callsign, c.content.confidence
    WETA 100
    WMPB 100
    WWPB 100
    WHUT 100
    WFPT 100
    WVPY 100
    WMPT 100
    WGTV 80
    KRMA 80
    WTTW 80
    WTVS 0
    KCTS 0
    KSPS 0
    WGBH 0
    WNED 0


.. Note::

    The :mod:`related` method accepts two arguments. First one the relationship name and the second one the class name which uses a default value of None as a flag to signify the absense of the argument. In the above example we only used the relationship name but we can also pass the class name as follows:
        >>>     print c.related('related', 'Callsign').content.callsign, c.content.confidence
