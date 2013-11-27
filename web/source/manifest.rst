================
Pytroll manifest
================


Pytroll adding value for satellite users 
=========================================

Produce what users wants (needs!)
---------------------------------

Unexpected needs
~~~~~~~~~~~~~~~~

    * User requests are unpredictable and development time potentially long. A
      flexible development and production system is needed in order to honor
      user requests in reasonable time when they are made.

    * Own software development is needed in order to be able to create highly
      specialized products.

Users unaware of possibilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - A gap exists between the domain users knowledge and the satellite
      developers knowledge of sensors technical capabilities. This leads to
      lack of knowledge of potential satellite data applications within a
      specific domain.

    - A communication and analysis effort is needed in order to start briding the gap.

    - The current (and for the foreseeable future) existence of the knowledge
      gap means the satellite software development needs to be planning ahead
      as users have limited capability to foresee the usage of future satellite
      data types.

Enable users to discover existing data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Inability for users to efficiently discover data means resources are
      wasted when users use time retrieving data elsewhere

    - Inability to efficiently query meta-data and geographical coverage means
      users waste time retrieving and filtering away unneeded datasets

    - External systems creating meta-data based on actual file contents is
      processing intense leading to higher energy consumption

Integrate externally developed software gracefully
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Satellite data processing is dependent on third party software
      packages. These needs to be integrated in a consistent way in order to
      limit development effort.

    - A consistent integration approach allows for sharing of package
      integrators between institutes saving duplicate development effort.

Interface for internally developed software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - A typically seen approach is for researchers to develop a full processing
      chain when creating a new product. As researchers are not trained
      software developers this typically leads to poor handling of the
      processing outside the scientific core of the processing chain as well as
      not integrating with existing production environments. A major rewrite of
      the software is normally needed in order to start production.

    - This process does not add any value to the end user of the product. With
      the existence of a well defined interface for a scientific core the
      researchers can focus on creating modules adhering to this interface and
      the development efforts to bring such a module into production will be
      very limited.

Rapid development response
--------------------------

Short article-to-production time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * The shortest possible time from product requirements definition to a
      final product in operations maximizes the value for end users as
      development response time decreases and more products can be put into
      production within a given time frame.

    * A framework is needed for developing satellite data processing that will limit
      the amount of development resources spent on repetitive development.

    * An easily configurable production environment will limit the amount of
      resources spent on configuration and maintenance.

Why Python?
~~~~~~~~~~~

The programming language Python has been chosen since it

    * accomodates rapid development

    * is widely used for scientific applications

    * has good numerical performance

    * is easy to use and understand for beginners

    * is very flexible for experienced software programmers

Crisis handling
~~~~~~~~~~~~~~~

    * Rapid prototyping and production integration allows for usage of
      satellite products in case of crisis (volcano eruptions and similar
      single upset events).


Production system resilience
----------------------------

High reliability and timeliness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Software development of high quality is needed due to requirements on
      data reliability and timeliness.

    * Levering existing knowledge of developing suitable software

Inter institution backup of key data sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Backup of locally received data and derived products

    * Full coverage of these kind of centrally produced products is unlikely to
      happen in a foreseeable future.


Efficient resource usage
------------------------

 * Sharing of software components removes duplicate software development efforts

    * Satellite data processing is very similar at meteorological
      services. Using the same software platform eliminates duplicate software
      development for the same functionality.

    * The more partners involved in the development the greater the resource
      saving effect.

 * Sharing of processing intense products reduces energy consumption and
   resource usage on configuration and maintenance

    * Not co-producing processing intense products (typically products derived
      from local reception not accessible from a central processing facility)
      at institutes saves processing resources and thereby energy.

    * Saving resources not configuring and maintaining all processing systems
      frees up resources for development.

 * The choice of free and open source is deliberately taken to support
   efficient sharing of development resources and make the software easily
   accessible to users. Open source code projects stimulates collaboration, and
   more easily generates positive spin offs. Also, exposing the code to the
   open source community results in software of higher quality (high demands on
   stability, easy installation, good documentation, etc).


Pytroll successes
-----------------

 * Framework created for satellite data processing (mpop et al.).

 * VIIRS (S-NPP) ready before launch. Very limited effort to add level1 and
   upstream processing to the framework.

 * mpop replacing comercial ill-fitting systems, adding flexibility,
   consistency and saving cost and processing resources.

 * Trollcasting: Efficient, secure and flexible data exchange. Being set up
   among the National Met Services. Interests from Canada and EUMETSAT (EARS
   team) among others.

 * Open Source approach extending usage and possible collaboration. Operational
   at Iceland, besides Denmark and Sweden. Being put in operation at FMI,
   Finland. The user base is global (Asia, USA, Canada, South America,
   Europe).
