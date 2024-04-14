import os
import json
import sys
import shutil
from datetime import datetime, timedelta

import flask
from flask import render_template, url_for, redirect, Response
from sqlalchemy.sql.expression import func
from data.cards import Card
from data.user import User


def get_duration(then: datetime, now=datetime.now()) -> str:

    duration = now - then
    duration_in_s = duration.total_seconds()

    def years() -> tuple[float, float]:
        return divmod(duration_in_s, 31536000)

    def days(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 86400)

    def hours(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 3600)

    def minutes(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 60)

    def seconds(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 1)

    def total_duration() -> str:
        y: tuple = years()
        d: tuple = days(y[1])
        h: tuple = hours(d[1])
        m: tuple = minutes(h[1])
        s: tuple = seconds(m[1])

        return (f"{int(y[0])} years, {int(d[0])} days, {int(h[0])} hours, "
                f"{int(m[0])} minutes and {int(s[0])} seconds")
    return total_duration()



