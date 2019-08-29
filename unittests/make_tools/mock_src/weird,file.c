/*
 * Copyright (c) 2018 The University of Manchester
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

// this is just test stuff and not real c

#include <debug.h>

static String woops = "log_info(";

    String naughty = "what is this /* nonsense"

    /* log_info("inside a comment */

    log_info("this is ok");

    //log_info("this is just a comment");

    log_info("this is fine "
             "on two lines");

    log_info("before comment "
    // a comment
             "after comment");

    log_info("One line commted"); //blah blah

    log_info("this is for alan); so there!");

    log_info("Test %u for alan); so there!",
        2);

    log_info(
        "\t back off = %u, time between spikes %u",
        random_backoff, time_between_spikes); // And a Comment

    for (int i = 0; i < NUM_EXCITATORY_RECEPTORS; i++){
        log_debug("the neuron %d has been determined to not spike",
                          neuron_index);
    }

    for (int i = 0; i < NUM_EXCITATORY_RECEPTORS; i++){
        log_warning("Inside a loop");  }

    log_info("then a space")   ;

    log_info("then a newline simple")
    ;

    log_info("then a newline plus")
    ; String more = "fluff";

    log_info("first"); log_info("second %u", 1234);
    log_info("then a backslash comment on a middle line")
    // comment
    ;

    log_info("then a standard comment on a middle line")
    /* comment */
    ;

    /* comment */ log_info("comment before");

    fluff fluff

    two = 2; log_info("two %u", two);