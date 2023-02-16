/*
 * Copyright (c) 2018 The University of Manchester
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// this is just test stuff and not real c

#include <debug.h>

static String woops = "log_info(";

    log_debug("%08x [%3d: (w: %5u (=",
                synapse, i, synapse_row_sparse_weight(synapse));

    String naughty = "what is this /* nonsense"

    /* log_info("inside a comment */

    log_info("test -three %f", -3.0f);

    log_info("test double %F", -3.0d);

    log_info("test slash // %f", 3/2);

    log_info("this is ok");

    //log_info("this is just a comment");

    log_info("this is fine "
             "on two lines");

    log_info("before comment "
    // a comment
             "after comment");

    log_info("One line commented"); //blah blah

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
    /* evil comment */
    ;

    log_info("then a empty line in the middle line")

    ;
    log_info("neuron_initialise: starting");
    log_info("test -two %f", -2.0f);
    log_info("test -one %f", -1.0f);
    log_info("test zero %x", 0.0f);
    log_info("test one %x", 1.0f);
    log_info("test two %x", 2.0f);
    log_info("test string comma, %u is fluff ", 12);
    log_info("test double percent %%s in string, %u fluff", 45);
    log_info("test string quote \" in string, %u fluff", 45);
    log_info("test string bacKslash %s fluff", "Rowley \" wins");
    log_info("test string comma %s fluff ", "Rowley, wins");
    log_info("test string comma, %u is fluff ", 12);
    log_info("test string many comma %s fluff ",
        "Rowley, wins, even more ( fluff");

    log_info("magic = %08x, version = %d.%d", ds_regions->magic_number,
            ds_regions->version >> VERSION_SHIFT,
            ds_regions->version & VERSION_MASK);

    log_inf("blah",
            ")",
            "more");
    /* comment */ log_info("comment before");

    fluff fluff

    two = 2; log_info("two %u", two);

    log_info("nospace %u%u", 1, 2);

    log_info("this is a float %f fluff", 1.0);

    log_debug("dumping into sorted at index %d proc %d, for key %d and "
        "has redundant packet count of %d",
        *sorted_bf_fill_loc, coverage[i]->processor_ids[bf_index],
        coverage[i]->bit_field_addresses[bf_index]->key,
        detect_redundant_packet_count(
        *coverage[i]->bit_field_addresses[bf_index],
        region_addresses));

    log_info("1:%u 2:%u 3:%u 4:%u 5:%u 6:%u 7:%u 8:%u 9:%u 10:%u"
             "11:%u 12:%u 13:%u 14:%u 15:%u 16:%u 17:%u 18:%u 19:%u 20:%u",
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
              11, 12, 13, 14, 15, 16, 17, 18, 19, 20);

    the end