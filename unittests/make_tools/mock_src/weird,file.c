// this is just test stuff and not real c

#include <debug.h>

static String woops = "log_info(";

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