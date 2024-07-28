
# GPUTILS PYTHON LIBRARY

A project that includes a SpellChecker for correcting text and a Security module for managing user authentication and database connections.

## Features

### SpellChecker
- Read a corpus file and calculate word probabilities.
- Generate candidate corrections for misspelled words using level one, two, and three edits.
- Return the most likely corrections based on word probabilities.

### Security
- Manage user authentication with a pickle-based auth object.
- Add, delete, and list users.
- Handle user login and registration with MySQL and MS-SQL databases.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rahulkher/gputils.git
cd projectname
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### SpellChecker

1. Ensure you have a corpus file (e.g., `words.txt`) in the root directory of the project. This file should contain a large number of words to build the vocabulary and calculate word probabilities.

2. Use the `SpellChecker` class in your Python script:

```python
from text_utils import SpellChecker

# Initialize the spell checker with the path to the corpus file
checker = SpellChecker(corpus_file_path="words.txt")

# Example passage
passage = "my name is rahul kher. how are you? what are toyu doing today. I wanna eat biryani. Thajs"
correct_passage = []
for word in passage.split(" "):
    if word not in checker.vocabs:
        try:
            word = checker.check(word)[0][0]
        except:
            word = word

    correct_passage.append(word)

final_passage = " ".join(correct_passage)

print(f"Wrong Passage: {passage}")
print()
print(f"Correct Passage: {final_passage}")
```

3. Run the script to see the corrected passage:

```bash
python your_script.py
```

### Security

1. Use the `StreamlitAuthObject` class to manage user authentication:

```python
from security import StreamlitAuthObject

# Initialize the auth object
auth = StreamlitAuthObject()

# Add a user
response = auth.adduser(username="newuser", email="newuser@mail.com", password="newpass123", role="user")
print(response)

# Delete a user
response = auth.delete_user(username="newuser")
print(response)

# List users
users = auth.list_users()
print(users)
```

2. Use the `StandardAuth` class to handle user login and registration with a database:

```python
from security import StandardAuth

# Initialize the StandardAuth object
user = StandardAuth(username="newuser", email="newuser@mail.com", password="newpass123", role="user", status=1, new_user=True)

# Connect to a database
connection = user._connect_DB(db_type="mysql", host_name="localhost", user_name="root", user_password="password", db_name="testdb")
print(connection['status'])

# Register the user in the database
response = user.register_user(users_tbl_name="users", user_tbl_exists=True, **connection)
print(response)

# Log in the user
login_response = user.login_user(users_tbl_name="users", **connection)
print(login_response)
```

## Example

Here is an example script that uses both the `SpellChecker` and `StreamlitAuthObject` classes:

```python
if __name__ == "__main__":
    # SpellChecker example
    from text_utils import SpellChecker

    checker = SpellChecker(corpus_file_path="words.txt")
    passage = "my name is rahul kher. how are you? what are toyu doing today. I wanna eat biryani. Thajs"
    correct_passage = []
    for word in passage.split(" "):
        if word not in checker.vocabs:
            try:
                word = checker.check(word)[0][0]
            except:
                word = word

        correct_passage.append(word)

    final_passage = " ".join(correct_passage)

    print(f"Wrong Passage: {passage}")
    print()
    print(f"Correct Passage: {final_passage}")

    # Security example
    from security import StreamlitAuthObject

    auth = StreamlitAuthObject()
    response = auth.adduser(username="newuser", email="newuser@mail.com", password="newpass123", role="user")
    print(response)

    response = auth.delete_user(username="newuser")
    print(response)

    users = auth.list_users()
    print(users)
```

## Contributing

Contributions are welcome! Please open an issue to discuss what you would like to change or add.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
