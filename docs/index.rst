.. Citizen Voice documentation master file, created by
   sphinx-quickstart on Mon Oct 27 15:47:24 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Citizen Voice documentation
===========================

An inclusive, web-based software platform for collaborative data collection that facilitates citizen participation.

Main Features
-----------------

- **Citizen Mapping**: A tool to create questionnaires and collect geo-spatial and non geo-spatial data about citizens' perceptions of their urban environment.
- **Community Dashboard**: A dashboard to visualize geo-spatial data collected through the Citizen Mapping tool, allowing for insights into community concerns and priorities.
- **Application Programming Interfaces (API)**: RESTful APIs that allows for the integration of the Citizen Voice platform with other applications, enabling data exchange and interoperability.

.. toctree::
   :maxdepth: 2
   
   overview

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user/installation
   user/creating_surveys
   user/ethical_guidelines

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   developer/quickstart-dev
   developer/development_workflow
   developer/overview
   developer/apis
   developer/citizen-mapping
   developer/community-dashboard
