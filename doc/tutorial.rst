Getting started
============================================================

This tutorial aims to get you started with resty as quickly as possible.

It is made up of a number of examples of increasing complexity, each of which shows one or more useful resty features.

If you have any comments about these tutorials, or suggestions for things we should cover in them, then please contact us via `Github <https://github.com/pbs/resty/>`_


Step 1: Configure the client
----------------------------

:mod:`resty` provides two types of clients:

* the default client - uses summaries if available therefore the interactions with the api are much faster

* dumb_client - does not use summaries and relies strictly on links


.. Note::

    Summary of the resource can be available as additional attributes on the collection


Step 2: Load the entrypoint and select a service
------------------------------------------------

The URL where the Service document is located is named the API Entrypoint.
In the provided example we use the sodor api url as an entrypoint and selecting the zipcode service from the available services.

::

    >>> from resty import client
    >>> c = client.load("http://services.pbs.org/")

    >>> zipcode_service = c.service("zipcodes")
    <resty.types.Collection object at 0x2597e90>


Step 3: Use filters
-------------------

The *$filters* are used to describe complex interactions that usually require some sort of human input. One particularly common situation is searching trough the elements of a collection. Templates are available only in collections. Since *zipcode_service* returns a collection object we can filter it based on zip.

::

    >>> filtered_zipcodes = zipcode_service.filter('zip', zipcode='22202')


.. Note::

    You need to pass to filter method the filter name (*zip*) and as **kwargs the placeholder name (*zipcodes*) with desired value (*22202*)


Step 4: Iterating through items
-------------------------------

Items represents the list of objects available in that collection. In the above example the *filtered_zipcodes* returns a collection with a single object. Let's select the first object from the list:

::

    >>> zipcode_resource = filtered_zipcodes.items()[0]
    >>> zipcode_resource
    <resty.types.Resource object at 0x259fc50>


Step 5: Accessing metadata and usefull content
----------------------------------------------

At this point we have a *zipcode_resource* and we can extract informations like metadata and content specific informations

::

    >>> print zipcode_resource.content.zipcode
    u'22202'
    >>> print zipcode_resource.class_
    u'Zipcode'



.. Note::

    All properties which are prefixed with $ are considered metadata



Step 6: Using links to interact with available relationships
------------------------------------------------------------

The $links property groups together all the relationships the resource identified by the $self attribute that is located on the same level with the $links property has.

The available relationships for the zipcode resource are:

* search   -> returns callsigns for the current zipcode
* related  -> returns states for the current zipcode
* presence -> returns headens for the current zipcode

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


Conclusion
----------

resty is:

* simple high-level API interaction
* easy to use
* smart
* supports multiple api rendering templates
