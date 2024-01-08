import Run
from pathlib import Path
# import os
import sys
# while True:
#     text = input("PyLang -> ")
#     if text.strip() == '':
#         continue
#     result, error = Run.run('<input>', text)
#
#     if error:
#         print(error.as_string())
#     elif result:
#         if len(result.elements) == 1:
#             print(repr(result.elements[0]))
#         else:
#             print(repr(result))


text = "run(\"" + sys.argv[1] + "\")"
result, error = Run.run(sys.argv[1], text)

# if error:
#     print(error.as_string())
# elif result:
#     if len(result.elements) == 1:
#         print(repr(result.elements[0]))
#     else:
#         print(repr(result))
