#!/usr/bin/env python

"""Execute a command."""

import sys

import anyio

import dagger


async def test():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        src = client.host().directory(".")

        # cache python dependencies into a shared volume
        buildout_cache = client.cache_volume("buildout")
        python_cache = client.cache_volume("python")

        python = (
            client.container()
            .from_("python:2.7.18-buster")
            .with_directory("/src", src, exclude=["dagger"])
            .with_mounted_cache("/cache", python_cache)
            .with_mounted_cache("/buildout", buildout_cache)
            .with_env_variable("XDG_CACHE_HOME", "/cache")
            .with_exec(["python", "--version"])
            .with_exec(["pip", "install", "virtualenv"])
            .with_exec(["virtualenv", "--version"])
            .with_exec(["virtualenv", "/src"])
            .with_exec(["/src/bin/pip", "install", "--upgrade", "pip"])
            .with_exec(["/src/bin/pip", "install", "zc.buildout"])
            .with_exec(["/src/bin/buildout", "-vv", "buildout:download-cache=/buildout/download", "buildout:eggs-directory=/buildout/eggs", "-c", "/src/buildout.cfg", "install", "test"])
            .with_exec(["/src/bin/test", "-s", "archetypes.schemaextender"])
        )

        # execute
        version = await python.stdout()

    print(f"Hello from Dagger and {version}")


anyio.run(test)
