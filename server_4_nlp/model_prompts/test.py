from poml import poml

markup_content = """
<poml>
  <role>You are a helpful assistant.</role>
  <task>Summarize the following text:</task>
  <text>The quick brown fox jumps over the lazy dog.</text>
</poml>
"""

result = poml(markup=markup_content)
print(result)