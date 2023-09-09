#!/usr/bin/env python

"""Execute a command."""

import sys

import anyio

import dagger
import tempfile

from pathlib import Path


async def test(hostdir: str):
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        src = client.host().directory(".")

        python = (
            client.container()
            .from_("python:2.7.18-buster")
            .with_directory("/src", src, exclude=["dagger", "python_cache", "buildout_cache"])
            .with_exec(["mkdir", "-p", "cache/buildout"])
            .with_exec(["mkdir", "-p", "cache/python"])
            .with_env_variable("XDG_CACHE_HOME", "/src/cache/python")
            .with_exec(["python", "--version"])
            .with_exec(["pip", "install", "virtualenv"])
            .with_exec(["virtualenv", "--version"])
            .with_exec(["virtualenv", "/src"])
            .with_exec(["/src/bin/pip", "install", "--upgrade", "pip"])
            .with_exec(["/src/bin/pip", "install", "zc.buildout"])
            .with_exec(["/src/bin/buildout", "-vv",
                        "buildout:download-cache=/src/cache/buildout/download",
                        "buildout:eggs-directory=/src/cache/buildout/eggs", "-c", "/src/buildout.cfg", "install", "test"])
            .with_exec(["/src/bin/test", "-s", "archetypes.schemaextender"])
            .directory("/src/cache")
            .export(hostdir)

        )

        await python


anyio.run(test, '/tmp/output-dagger')
