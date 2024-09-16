-- Copyright (c) 2018 The University of Manchester
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     https://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- https://www.sqlite.org/pragma.html#pragma_synchronous
PRAGMA main.synchronous = OFF;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
-- A table holding each log message
CREATE TABLE IF NOT EXISTS log(
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level INTEGER NOT NULL,
    line_num INTEGER NOT NUll,
	original STRING NOT NULL,
    file_id  STRING NOT NULL REFERENCES file(file_id) ON DELETE RESTRICT
	);

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
-- A table holding data on the converted file
CREATE TABLE IF NOT EXISTS file(
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_id INTEGER NOT NULL REFERENCES directory(directory_id) ON DELETE RESTRICT,
	file_name STRING NOT NULL,
    convert_time INTEGER,
    last_build INTEGER
	);

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
-- A table holding data on the converted file
CREATE TABLE IF NOT EXISTS directory(
    directory_id INTEGER PRIMARY KEY AUTOINCREMENT,
	src_path STRING NOT NULL,
	dest_path STRING NOT NULL
	);

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
-- Glue the bits together to show the information that people think is here
CREATE VIEW IF NOT EXISTS current_file_view AS
    SELECT log_id, log_level, file_name, line_num , original, file_id, src_path, dest_path, convert_time
    FROM log NATURAL JOIN file NATURAL JOIN directory
    WHERE last_build = 1;

CREATE VIEW IF NOT EXISTS all_file_view AS
    SELECT log_id, log_level, file_name, line_num , original, file_id, src_path, dest_path, convert_time
    FROM log NATURAL JOIN file;
