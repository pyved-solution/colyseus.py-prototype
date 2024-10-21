# colyseus.py-prototype

In this repo you will find my own study of the colyseus state sync mechanism, mostly in python &amp; attempt to use ws for interoperability. For most people this won't be useful as this is too experimental.

## Getting started

- if you wish to perform online analysis, in general `npm install` followed by `npm run start` is enough.

## A few ideas

- use an ancient version to avoid the "schema" serializer for easier prototyping using py
- fork the current ColyseusJS and modify it to use plain JS objects for state synchronization
- use a schema generator for py that produces dataclasses only

## Useful links

Old releases of Colyseus:
- https://github.com/colyseus/colyseus/releases?page=2
I don't know at what point the "schema" serializer has been introducted

Alternatives to the schema serializer:
- https://www.npmjs.com/package/msgpackr
