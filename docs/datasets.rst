Datasets
========

BICAM provides access to 12 comprehensive congressional and legislative datasets. Each dataset is carefully curated and includes metadata, text content, and related records.

Dataset Overview
---------------

+------------------------+------------+----------------+------------------+
| Dataset                | Size       | Congress Range | Description      |
+========================+============+================+==================+
| bills                  | ~2.5GB     | 93-118         | Complete bills   |
+------------------------+------------+----------------+------------------+
| amendments             | ~800MB     | 93-118         | All amendments   |
+------------------------+------------+----------------+------------------+
| members                | ~150MB     | 1-118          | Member info      |
+------------------------+------------+----------------+------------------+
| nominations            | ~400MB     | 93-118         | Nominations      |
+------------------------+------------+----------------+------------------+
| committees             | ~200MB     | 93-118         | Committee info   |
+------------------------+------------+----------------+------------------+
| committeereports       | ~1.2GB     | 104-118        | Committee reports|
+------------------------+------------+----------------+------------------+
| committeemeetings      | ~600MB     | 110-118        | Meeting records  |
+------------------------+------------+----------------+------------------+
| committeeprints        | ~900MB     | 105-118        | Committee prints |
+------------------------+------------+----------------+------------------+
| hearings               | ~3.5GB     | 105-118        | Hearing records  |
+------------------------+------------+----------------+------------------+
| treaties               | ~300MB     | 93-118         | Treaty documents |
+------------------------+------------+----------------+------------------+
| congresses             | ~100MB     | 1-119          | Session metadata |
+------------------------+------------+----------------+------------------+
| complete               | ~12GB      | 1-119          | All datasets     |
+------------------------+------------+----------------+------------------+

Bills Dataset
------------

**Description**: Complete bills data including text, summaries, and related records

**Files**:

+-----------------------+-------------------------------------------------------------+
| File                  | Description                                                 |
+=======================+=============================================================+
| bills_metadata.csv    | Bill metadata (sponsor, dates, status, etc.)                |
+-----------------------+-------------------------------------------------------------+
| bills_texts.csv       | Full text of bills                                          |
+-----------------------+-------------------------------------------------------------+
| bills_sponsors.csv    | Sponsor information                                         |
+-----------------------+-------------------------------------------------------------+

**Key Fields**:

+-------------------+-----------------------------------------------+
| Field             | Description                                   |
+===================+===============================================+
| bill_id           | Unique bill identifier                        |
+-------------------+-----------------------------------------------+
| congress          | Congress number (93-118)                      |
+-------------------+-----------------------------------------------+
| bill_type         | Type of bill (HR, S, etc.)                    |
+-------------------+-----------------------------------------------+
| title             | Bill title                                    |
+-------------------+-----------------------------------------------+
| sponsor_id        | Sponsor's member ID                           |
+-------------------+-----------------------------------------------+
| introduced_date   | Date introduced                               |
+-------------------+-----------------------------------------------+
| status            | Current status                                |
+-------------------+-----------------------------------------------+

Amendments Dataset
-----------------

**Description**: All amendments with amended items

**Files**:

+--------------------------+----------------------+
| File                     | Description          |
+==========================+======================+
| amendments_metadata.csv  | Amendment metadata   |
+--------------------------+----------------------+
| amendments_texts.csv     | Amendment text       |
+--------------------------+----------------------+

**Key Fields**:

+-------------------+-------------------------------+
| Field             | Description                   |
+===================+===============================+
| amendment_id      | Unique amendment identifier   |
+-------------------+-------------------------------+
| bill_id           | Associated bill               |
+-------------------+-------------------------------+
| congress          | Congress number               |
+-------------------+-------------------------------+
| amendment_type    | Type of amendment             |
+-------------------+-------------------------------+
| sponsor_id        | Amendment sponsor             |
+-------------------+-------------------------------+
| text              | Amendment text                |
+-------------------+-------------------------------+

Members Dataset
--------------

**Description**: Historical and current member information

**Files**:

+--------------------------+------------------------+
| File                     | Description            |
+==========================+========================+
| members_current.csv      | Current members        |
+--------------------------+------------------------+
| members_historical.csv   | Historical members     |
+--------------------------+------------------------+
| members_committees.csv   | Committee memberships  |
+--------------------------+------------------------+

**Key Fields**:

+--------------+------------------------+
| Field        | Description            |
+==============+========================+
| member_id    | Unique member identifier|
+--------------+------------------------+
| name         | Member name            |
+--------------+------------------------+
| state        | State represented      |
+--------------+------------------------+
| party        | Political party        |
+--------------+------------------------+
| chamber      | House or Senate        |
+--------------+------------------------+
| start_date   | Term start date        |
+--------------+------------------------+
| end_date     | Term end date          |
+--------------+------------------------+

Nominations Dataset
------------------

**Description**: Presidential nominations data

**Files**:

+---------------------------+----------------------+
| File                      | Description          |
+===========================+======================+
| nominations_metadata.csv  | Nomination metadata |
+---------------------------+----------------------+
| nominations_actions.csv   | Nomination actions  |
+---------------------------+----------------------+

**Key Fields**:

+-------------------+-------------------------------+
| Field             | Description                   |
+===================+===============================+
| nomination_id     | Unique nomination identifier  |
+-------------------+-------------------------------+
| nominee_name      | Nominee name                  |
+-------------------+-------------------------------+
| position          | Position nominated for        |
+-------------------+-------------------------------+
| president         | Nominating president          |
+-------------------+-------------------------------+
| status            | Nomination status             |
+-------------------+-------------------------------+
| action_date       | Action date                   |
+-------------------+-------------------------------+

Committees Dataset
-----------------

**Description**: Committee information, including history of committee names

**Files**:

+----------------------------+------------------------+
| File                       | Description            |
+============================+========================+
| committees_metadata.csv    | Committee metadata     |
+----------------------------+------------------------+
| committees_membership.csv  | Committee memberships  |
+----------------------------+------------------------+

**Key Fields**:

+---------------+-------------------------------+
| Field         | Description                   |
+===============+===============================+
| committee_id  | Unique committee identifier   |
+---------------+-------------------------------+
| name          | Committee name                |
+---------------+-------------------------------+
| chamber       | House or Senate               |
+---------------+-------------------------------+
| type          | Committee type                |
+---------------+-------------------------------+
| member_id     | Member ID                     |
+---------------+-------------------------------+
| role          | Member role in committee      |
+---------------+-------------------------------+

Committee Reports Dataset
------------------------

**Description**: Committee reports, with full text and related information

**Files**:

+----------------------+----------------------------------------+
| File                 | Description                            |
+======================+========================================+
| reports_metadata.csv | Report metadata                        |
+----------------------+----------------------------------------+
| reports_text.json    | Report text (JSON format)              |
+----------------------+----------------------------------------+

**Key Fields**:

+---------------+-------------------------------+
| Field         | Description                   |
+===============+===============================+
| report_id     | Unique report identifier      |
+---------------+-------------------------------+
| committee_id  | Committee ID                  |
+---------------+-------------------------------+
| congress      | Congress number               |
+---------------+-------------------------------+
| report_number | Report number                 |
+---------------+-------------------------------+
| title         | Report title                  |
+---------------+-------------------------------+
| text          | Full report text              |
+---------------+-------------------------------+

Committee Meetings Dataset
-------------------------

**Description**: Committee meeting records

**Files**:

+--------------------------+----------------------+
| File                     | Description          |
+==========================+======================+
| meetings_metadata.csv    | Meeting metadata     |
+--------------------------+----------------------+
| meetings_attendance.csv  | Meeting attendance   |
+--------------------------+----------------------+

**Key Fields**:

+---------------------+-------------------------------+
| Field               | Description                   |
+=====================+===============================+
| meeting_id          | Unique meeting identifier     |
+---------------------+-------------------------------+
| committee_id        | Committee ID                  |
+---------------------+-------------------------------+
| date                | Meeting date                  |
+---------------------+-------------------------------+
| title               | Meeting title                 |
+---------------------+-------------------------------+
| member_id           | Member ID                     |
+---------------------+-------------------------------+
| attendance_status   | Attendance status             |
+---------------------+-------------------------------+

Committee Prints Dataset
-----------------------

**Description**: Committee prints, including full text and topics

**Files**:

+-------------------------------+----------------------+
| File                          | Description          |
+===============================+======================+
| committeeprints_metadata.csv  | Print metadata       |
+-------------------------------+----------------------+
| committeeprints_texts.csv     | Print text           |
+-------------------------------+----------------------+

**Key Fields**:

+--------------+-------------------------------+
| Field        | Description                   |
+==============+===============================+
| print_id     | Unique print identifier       |
+--------------+-------------------------------+
| committee_id | Committee ID                  |
+--------------+-------------------------------+
| congress     | Congress number               |
+--------------+-------------------------------+
| title        | Print title                   |
+--------------+-------------------------------+
| text         | Print text                    |
+--------------+-------------------------------+
| topics       | Associated topics             |
+--------------+-------------------------------+

Hearings Dataset
---------------

**Description**: Hearing information, such as address and transcripts

**Files**:

+------------------------+----------------------+
| File                   | Description          |
+========================+======================+
| hearings_metadata.csv  | Hearing metadata     |
+------------------------+----------------------+
| hearings_texts.csv     | Hearing transcripts  |
+------------------------+----------------------+

**Key Fields**:

+--------------+-------------------------------+
| Field        | Description                   |
+==============+===============================+
| hearing_id   | Unique hearing identifier     |
+--------------+-------------------------------+
| committee_id | Committee ID                  |
+--------------+-------------------------------+
| congress     | Congress number               |
+--------------+-------------------------------+
| title        | Hearing title                 |
+--------------+-------------------------------+
| date         | Hearing date                  |
+--------------+-------------------------------+
| text         | Hearing transcript            |
+--------------+-------------------------------+

Treaties Dataset
---------------

**Description**: Treaty documents with actions, titles, and more

**Files**:

+------------------------+----------------------+
| File                   | Description          |
+========================+======================+
| treaties_metadata.csv  | Treaty metadata      |
+------------------------+----------------------+
| treaties_actions.csv   | Treaty actions       |
+------------------------+----------------------+

**Key Fields**:

+--------------+-------------------------------+
| Field        | Description                   |
+==============+===============================+
| treaty_id    | Unique treaty identifier      |
+--------------+-------------------------------+
| title        | Treaty title                  |
+--------------+-------------------------------+
| congress     | Congress number               |
+--------------+-------------------------------+
| action_type  | Action type                   |
+--------------+-------------------------------+
| action_date  | Action date                   |
+--------------+-------------------------------+
| status       | Treaty status                 |
+--------------+-------------------------------+

Congresses Dataset
-----------------

**Description**: Congressional session metadata, like directories and session dates

**Files**:

+---------------------------------+-----------------------------+
| File                            | Description                 |
+=================================+=============================+
| congresses.csv                  | Congress metadata           |
+=================================+=============================+
| congresses_directories.csv      | Congressional directories   |
+=================================+=============================+
| congresses_directories_isbn.csv | Directory ISBNs             |
+=================================+=============================+
| congresses_sessions.csv         | Session information         |
+=================================+=============================+

**Key Fields**:

+-------------+-------------------------------+
| Field       | Description                   |
+=============+===============================+
| congress    | Congress number               |
+-------------+-------------------------------+
| start_date  | Session start date            |
+-------------+-------------------------------+
| end_date    | Session end date              |
+-------------+-------------------------------+
| session     | Session number                |
+-------------+-------------------------------+
| member_id   | Member ID                     |
+-------------+-------------------------------+
| name        | Member name                   |
+-------------+-------------------------------+

Complete Dataset
---------------

**Description**: Complete BICAM dataset with all data types

**Files**: All files from individual datasets

**Size**: ~12GB


Data Formats
-----------

All datasets are provided in CSV format for easy analysis with pandas, R, or other data analysis tools.

- **CSV Files**:
  - UTF-8 encoded
  - Comma-separated values
  - Header row included
  - Consistent field naming


Data Quality
-----------

- **Completeness**: Data covers the full specified congress range
- **Accuracy**: Data sourced from official government sources
- **Consistency**: Consistent field names and formats across datasets
- **Timeliness**: Updated regularly with new congressional sessions

Data Updates
-----------

Datasets are updated as new congressional data becomes available. Check the dataset information for the latest update dates:

.. code-block:: bash

   bicam info bills
