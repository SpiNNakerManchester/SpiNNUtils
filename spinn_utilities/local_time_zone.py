# Copyright (c)  The University of Manchester
# Based on example from docs.python.org
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# source https://docs.python.org/3/library/datetime.html#tzinfo-objects

import time
from datetime import datetime, timedelta, tzinfo

ZERO = timedelta(0)
HOUR = timedelta(hours=1)
SECOND = timedelta(seconds=1)

STDOFFSET = timedelta(seconds=-time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds=-time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(tzinfo):
    """
    A class capturing the platform's idea of local time.

    (May result in wrong values on historical times in
    a time zone where UTC offset and/or the DST rules had
    changed in the past.)
    """

    def fromutc(self, dt: datetime) -> datetime:
        """
        datetime in UTC -> datetime in local time.

        :return: an equivalent datetime in self’s local time.
        """
        assert dt.tzinfo is self
        stamp = (dt - datetime(1970, 1, 1, tzinfo=self)) // SECOND
        args = time.localtime(stamp)[:6]
        dst_diff = DSTDIFF // SECOND
        # Detect fold
        fold = (args == time.localtime(stamp - dst_diff))
        return datetime(*args, microsecond=dt.microsecond,
                        tzinfo=self, fold=fold)

    def utcoffset(self, dt: datetime | None) -> timedelta:
        """
        Offset of local time from UTC
        Positive for east of UTC, negative for west of UTC

        :return: offset of local time from UTC
        """
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt: datetime | None) -> timedelta:
        """
        The daylight saving time (DST) adjustment

        Positive for east of UTC.

        Return 0 if DST not in effect.

        :return: the daylight saving time (DST) adjustment
        """
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt: datetime | None) -> str:
        """
        string name of time zone

        :return: the time zone name
        """
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt: datetime | None) -> bool:
        if dt is None:
            return False
        tt = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


LOCAL = LocalTimezone()
