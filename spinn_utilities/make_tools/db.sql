-- Copyright (c) 2018-2019 The University of Manchester
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
