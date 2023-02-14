/*
 * Copyright (c) 2013 The University of Manchester
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

/*! \file
 *
 *  \brief Bit field manipulation.
 *
 *  \details A bit field is a vector of machine words which is
 *    treated as a vector of bits.
 *
 *    For SpiNNAker each machine word is 32 bits, and so a
 *    bit_field for each neuron (assuming 256 neurons)
 *    would be 8 words long.
 *
 *    The API includes:
 *
 *     - bit_field_test (b, n)
 *         returns true of false depending on whether bit n is set or clear
 *     - bit_field_set (b, n) / bit_field_clear (b, n)
 *         used to set or clear bit n
 *     - not_bit_field (b, s)
 *         logically inverts a bit field of size s.
 *     - and_bit_field / or_bit_field
 *         logically ands/ors two bit_fields together. Requires size.
 *     - clear_bit_field/set_bit_field
 *         Initializes bit_field with all false (= clear) or true (= set).
 *         Requires size.
 *
 *    There are also support functions for:
 *
 *     - printing
 *     - randomly setting up a bit field
 *
 *  \author
 *    Dave Lester (david.r.lester@manchester.ac.uk),
 *    Jamie Knight (knightj@cs.man.ac.uk)
 *
 *  \copyright
 *    Copyright (c) Dave Lester, Jamie Knight and The University of Manchester,
 *    2013.
 *    All rights reserved.
 *    SpiNNaker Project
 *    Advanced Processor Technologies Group
 *    School of Computer Science
 *    The University of Manchester
 *    Manchester M13 9PL, UK
 *
 *  \date 12 December, 2013
 *
 *  DETAILS
 *    Created on       : 12 December 2013
 *    Version          : $Revision$
 *    Last modified on : $Date$
 *    Last modified by : $Author$
 *    $Id$
 *
 *    $Log$
 *
 */

#include "bit_field.h"
#include "sark.h"
#include "debug.h"

//! \brief This function prints out an individual word of a bit_field,
// as a sequence of ones and zeros.
//! \param[in] e The word of a bit_field to be printed.
static inline void print_bit_field_entry(
	uint32_t e)
{
    counter_t i = 32;

    for ( ; i > 0; i--) {
	log_debug("%c", ((e & 0x1) == 0) ? ' ' : '1');
	e >>= 1;
    }

    log_debug("\n");
}

//! \brief This function prints out an entire bit_field,
// as a sequence of ones and zeros.
//! \param[in] b The sequence of words representing a bit_field.
//! \param[in] s The size of the bit_field.
void print_bit_field_bits(
	bit_field_t b,
	size_t s)
{
    use(b);
    use(s);
#if LOG_LEVEL >= LOG_DEBUG
    index_t i; //!< For indexing through the bit field

    for (i = 0; i < s; i++) {
	print_bit_field_entry(b[i]);
    }
#endif // LOG_LEVEL >= LOG_DEBUG
}

//! \brief This function prints out an entire bit_field,
// as a sequence of hexadecimal numbers, one per line.
//! \param[in] b The sequence of words representing a bit_field.
//! \param[in] s The size of the bit_field.
void print_bit_field(
		bit_field_t b,
		size_t s)
{
    use(b);
    use(s);
#if LOG_LEVEL >= LOG_DEBUG
    index_t i; //!< For indexing through the bit field

    for (i = 0; i < s; i++) {
	log_debug("%08x\n", b[i]);
    }
#endif // LOG_LEVEL >= LOG_DEBUG
}

//! \brief This function generates a random bit_field.
//! \param[in] b The sequence of words representing a bit_field.
//! \param[in] s The size of the bit_field.

void random_bit_field(
		bit_field_t b,
		size_t s)
{
    use(b);
    use(s);
#if LOG_LEVEL >= LOG_DEBUG
    index_t i; //!< For indexing through the bit field

    for (i = 0; i < s; i++) {
	b[i] = sark_rand();
    }
#endif // LOG_LEVEL >= LOG_DEBUG
}
