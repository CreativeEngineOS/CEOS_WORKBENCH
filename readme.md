CEOS Workbench
A web application for managing a document-centric workflow, from raw content ingestion to final publication.

**Copyright © 2025, Bastiaan Slabbers/CEOS/OOgImages. All Rights Reserved. 
**No part of this project, including its content, code, or visual design, may be reproduced, distributed, or transmitted in any form or by any means, or be used to create derivative works, without prior written permission.

Key Features
Document Workflow: Manage documents through a clear, multi-stage process: Raw ➡️ Draft ➡️ Edited ➡️ Published.

Searchable Content Archive: A central hub to view, search, and filter all documents in the system.

Metadata Management: View and edit document metadata, including title, tags, and a synopsis, in a dedicated information panel.

Editor Notes: Attach comments to specific text selections within a document.

Integrated Style Guide: Maintain writing consistency by building a central repository of approved words and phrases.

File Ingestion System: Automatically process new files from a designated server folder and add them to the archive.

Customizable UI: Personalize the user interface by adjusting the theme, text size, and element spacing.

Architecture Overview
CEOS Workbench uses a modular, "actor-based" front-end architecture. Each "actor" is a Javascript module with a specific set of responsibilities, which keeps the code organized and easier to maintain.

The primary actors are:

main_actor.js: The central controller for the application. It initializes all other modules, loads data from the server, and manages the overall UI and user interactions.

metadata_actor.js: Controls the "Information" side panel. It is responsible for fetching, displaying, and saving the metadata for the selected document.

highlight_actor.js: Manages the right-click context menu in the text editor. It captures highlighted text to enable the "Add to Style Guide" and "Add Note" features.

The front-end communicates with a backend server through a RESTful API to handle data operations.

Core Concepts Explained
The Archive: The main screen of the application, which displays a list of all documents. From here, users can search, filter by status, and sort documents to quickly find what they need.

The Workflow: Documents move through a series of statuses, representing their journey from initial creation to final publication. The application provides buttons to promote a document from one stage to the next.

The VOID: A status for documents that have been rejected from the workflow. These documents are hidden from the main archive list but can be managed or permanently deleted from the settings panel.

Ingestion: The process of adding new documents to the Workbench. The system monitors a specific folder on the server (the "ingest folder") and automatically processes any new files it finds, adding them to the Archive with a "Raw" status.

Getting Started
Prerequisites
To run the CEOS Workbench front-end, you will need a local or remote web server capable of serving static files (HTML, CSS, Javascript) and a backend environment to host the API.

Installation
Clone the repository to your local machine.

Configure your web server to point to the project's root directory.

Ensure the backend API is running and accessible to the front-end application.

Configuration
API Endpoints: All API calls are relative paths (e.g., /api/metadata). You may need to configure a proxy if your API is hosted on a different domain or port.

Ingest Folder: The path to the ingest folder is set on the backend. Refer to the backend documentation for instructions on how to configure this setting.
