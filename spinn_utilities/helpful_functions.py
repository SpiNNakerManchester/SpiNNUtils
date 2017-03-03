import logging
import inspect
import re
import os
import datetime
import shutil

logger = logging.getLogger(__name__)
FINISHED_FILENAME = "finished"


def get_valid_components(module, terminator):
    """ Get possible components

    :param module:
    :param terminator:
    :rtype: dict
    """
    terminator = re.compile(terminator + '$')
    return dict(map(lambda (name, router): (terminator.sub('', name), router),
                inspect.getmembers(module, inspect.isclass)))


def set_up_output_application_data_specifics(
        where_to_write_application_data_files,
        max_application_binaries_kept, app_id, n_calls_to_run,
        this_run_time_string):
    """

    :param where_to_write_application_data_files:\
        the location where all app data is by default written to
    :param max_application_binaries_kept:\
        The max number of report folders to keep active at any one time
    :param app_id:\
        the id used for identifying the simulation on the SpiNNaker machine
    :param n_calls_to_run: the counter of how many times run has been called.
    :param this_run_time_string: the time stamp string for this run
    :return: the run folder for this simulation to hold app data
    """
    this_run_time_folder = None
    if where_to_write_application_data_files == "DEFAULT":
        directory = os.getcwd()
        application_generated_data_file_folder = \
            os.path.join(directory, 'application_generated_data_files')
        if not os.path.exists(application_generated_data_file_folder):
            os.makedirs(application_generated_data_file_folder)

        _remove_excess_folders(
            max_application_binaries_kept,
            application_generated_data_file_folder)

        # add time stamped folder for this run
        this_run_time_folder = os.path.join(
            application_generated_data_file_folder, this_run_time_string)
        if not os.path.exists(this_run_time_folder):
            os.makedirs(this_run_time_folder)

        # store timestamp in latest/time_stamp
        _write_timestamp(this_run_time_folder, app_id, this_run_time_string)

    elif where_to_write_application_data_files == "TEMP":

        # just don't set the config param, code downstairs
        # from here will create temp folders if needed
        pass
    else:

        # add time stamped folder for this run
        this_run_time_folder = os.path.join(
            where_to_write_application_data_files, this_run_time_string)
        if not os.path.exists(this_run_time_folder):
            os.makedirs(this_run_time_folder)

        # remove folders that are old and above the limit
        _remove_excess_folders(
            max_application_binaries_kept,
            where_to_write_application_data_files)

        # store timestamp in latest/time_stamp
        _write_timestamp(this_run_time_folder, app_id, this_run_time_string)

        if not os.path.exists(this_run_time_folder):
            os.makedirs(this_run_time_folder)

    # create sub folder within reports for sub runs (where changes need to be
    # recorded)
    this_run_time_sub_folder = os.path.join(
        this_run_time_folder, "run_{}".format(n_calls_to_run))

    if not os.path.exists(this_run_time_sub_folder):
        os.makedirs(this_run_time_sub_folder)

    return this_run_time_sub_folder, this_run_time_folder


def _write_timestamp(folder, app_id, timestamp):
    time_of_run_file_name = os.path.join(folder, "time_stamp")
    with open(time_of_run_file_name, "w") as writer:
        writer.writelines("app_{}_{}".format(app_id, timestamp))


def set_up_report_specifics(
        default_report_file_path, max_reports_kept, app_id, n_calls_to_run,
        this_run_time_string=None):
    """

    :param default_report_file_path: The location where all reports reside
    :param max_reports_kept:\
        The max number of report folders to keep active at any one time
    :param app_id:\
        the id used for identifying the simulation on the SpiNNaker machine
    :param n_calls_to_run: the counter of how many times run has been called.
    :param this_run_time_string: holder for the timestamp for future runs
    :return: The folder for this run, the time_stamp
    """

    # determine common report folder
    config_param = default_report_file_path
    created_folder = False
    if config_param == "DEFAULT":
        directory = os.getcwd()

        # global reports folder
        report_default_directory = os.path.join(directory, 'reports')
        if not os.path.exists(report_default_directory):
            os.makedirs(report_default_directory)
            created_folder = True
    elif config_param == "REPORTS":
        report_default_directory = 'reports'
        if not os.path.exists(report_default_directory):
            os.makedirs(report_default_directory)
    else:
        report_default_directory = os.path.join(config_param, 'reports')
        if not os.path.exists(report_default_directory):
            os.makedirs(report_default_directory)

    # clear and clean out folders considered not useful anymore
    if not created_folder and len(os.listdir(report_default_directory)) > 0:
        _remove_excess_folders(max_reports_kept, report_default_directory)

    # determine the time slot for later
    if this_run_time_string is None:
        this_run_time = datetime.datetime.now()
        this_run_time_string = (
            "{:04}-{:02}-{:02}-{:02}-{:02}-{:02}-{:02}".format(
                this_run_time.year, this_run_time.month, this_run_time.day,
                this_run_time.hour, this_run_time.minute,
                this_run_time.second, this_run_time.microsecond))

    # handle timing app folder and cleaning of report folder from last run
    app_folder_name = os.path.join(
        report_default_directory, this_run_time_string)

    if not os.path.exists(app_folder_name):
        os.makedirs(app_folder_name)

    # create sub folder within reports for sub runs (where changes need to be
    # recorded)
    app_sub_folder_name = os.path.join(
        app_folder_name, "run_{}".format(n_calls_to_run))

    if not os.path.exists(app_sub_folder_name):
        os.makedirs(app_sub_folder_name)

    # store timestamp in latest/time_stamp for provenance reasons
    _write_timestamp(app_folder_name, app_id, this_run_time_string)

    return app_sub_folder_name, app_folder_name, this_run_time_string


def write_finished_file(app_data_runtime_folder, report_default_directory):
    # write a finished file that allows file removal to only remove folders
    # that are finished
    app_file_name = os.path.join(app_data_runtime_folder, FINISHED_FILENAME)
    with open(app_file_name, "w") as writer:
        writer.writelines("finished")

    app_file_name = os.path.join(report_default_directory, FINISHED_FILENAME)
    with open(app_file_name, "w") as writer:
        writer.writelines("finished")


def _remove_excess_folders(max_to_keep, starting_directory):
    files_in_report_folder = os.listdir(starting_directory)

    # while there's more than the valid max, remove the oldest one
    if len(files_in_report_folder) > max_to_keep:

        # sort files into time frame
        files_in_report_folder.sort(
            cmp, key=lambda temp_file:
            os.path.getmtime(os.path.join(starting_directory, temp_file)))

        # remove only the number of files required, and only if they have
        # the finished flag file created
        num_files_to_remove = len(files_in_report_folder) - max_to_keep
        files_removed = 0
        for current_oldest_file in files_in_report_folder:
            finished_flag = os.path.join(os.path.join(
                starting_directory, current_oldest_file), FINISHED_FILENAME)
            if (os.path.exists(finished_flag) and
                    files_removed < num_files_to_remove):
                shutil.rmtree(
                    os.path.join(starting_directory, current_oldest_file),
                    ignore_errors=True)
                files_removed += 1
