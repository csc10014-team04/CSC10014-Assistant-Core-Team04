# Lab 4 - Reflection (H2)

Calling `service.handle()` in Lab 3 is a Python function call: the caller must be Python, in the same process,
with the package installed. `POST /v1/chat` is the same function behind the network: any client (browser, phone
app, test script, another language) sends JSON and gets JSON and a status code back, without importing our code.

A team prefers the HTTP version because the UI, mobile app and tests can be built in parallel against one stable
contract, the backend can change or scale without breaking them, and the API adds shared concerns in one place
(validation, error shape, rate limiting, admin key).
