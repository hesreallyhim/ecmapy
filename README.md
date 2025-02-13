# ecmapy

This project is intended to explore a proof-of-concept for how one might develop a (partial) bi-directional transpiler for python <-> JavaScript that would allow developers to use some of the most convenient syntactic features of modern JS in python (such as optional chaining, nullish coalescing, etc.), and also enable Javascript developers to use various python patterns (e.g. list comprehension). This project is in the exploratory phase. Functionality will be added incrementally, with the initial goal of enabling the optional chaining syntax (`foo?.bar?.baz()`) in python, and designing a transpilation workflow. Guiding constraints include:
* Avoid the need for wrapper functions like:

```python
class MyClass:
    def __init__(self):
        self.foo = "bar"

c = MyClass()
x = c.foo # x = "bar"
x = c.baz # raises `AttributeError`
# JAVASCRIPT WRAPPER APPROACH ❌
to_js("x = c?.baz") # x = None
```
Instead, prefer:
```python
c = MyClass()
x = c.foo # x = "bar"
# TRANSPILE THE BELOW TO SOMETHING LIKE:
x = c.foo # x = "bar"
x = c?.baz # x = c.get("baz", None); x = None
x = c.baz # raises `AtrributeError
```

* Enable the ecmapy code to work with linters, type-checkers, and IDE extensions.

* Enable seamless integration with existing CI/CD workflows.

## License

This project is licensed under the [GNU Affero General Public License](LICENSE) (AGPLv3).
