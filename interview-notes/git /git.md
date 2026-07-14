What does git init do?
Good answer:
"git init initializes a Git repository by creating a hidden .git directory. This directory stores all version control information such as commits, branches, and repository configuration."

Files
   │(git add .)
   ▼
Staging Area
   │( git commit)
   ▼
Commit(git commit -m "Initial project setup”)
(Git push)

Command	Purpose
git init	Initializes a Git repository by creating the hidden .git folder.
git branch -m main	Renames the current branch from master to main.
git add .	Stages all changes in the current directory.
git commit -m "message"	Creates a snapshot of the staged changes.
git push	Uploads commits to the remote GitHub repository.

1.git init converts a normal folder into a Git repository by creating a hidden .git directory where Git stores all version control information.
2..git folder stores Commit history,Branches,Tags,Repository configuration
3.git add . --It adds them to the staging area.
            git add . stages all new and modified files so they are ready to be committed.

Working Directory

↓

git add .

↓

Staging Area

↓

git commit

↓

Git History

4.Difference between git add and git commit?
-------------------------------

Git Flow

Imagine you're writing a book.

README.md

You edit it.

Where is it now?

Working Directory

Then:

git add .

Moves it here:

Staging Area

Then:

git commit -m "Added README"

Moves it here:

Git Repository (.git)

Still on your laptop.

Finally:

git push

Moves it here:

GitHub

### Real Architecute
Working Directory
       │
       ▼
git add .
       │
       ▼
Staging Area
       │
git commit
       │
       ▼
Local Repository (.git)
       │
git push
       │
       ▼
GitHub Remote Repository

5.What is the difference between git add, git commit, and git push?

Interview Answer
git add stages changes by moving them from the working directory to the staging area.
git commit creates a permanent snapshot of the staged changes in the local Git repository.
git push uploads those local commits to the remote repository, such as GitHub.