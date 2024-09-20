# Text-to-SQL Application using LlamaIndex, ChromaDB, and LLaMA Models

This project is a text-to-SQL application that converts natural language queries into SQL queries and executes them against a Microsoft SQL Server database. It uses LlamaIndex, ChromaDB, and LLaMA models to handle complex queries, multiple tables, conversation context, and entity ambiguity.

## **Table of Contents**

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## **Features**

- **Natural Language Processing**: Converts user queries into SQL.
- **Multiple Table Handling**: Supports queries across multiple tables and handles joins.
- **Conversation Context**: Maintains context to handle follow-up questions.
- **Entity Ambiguity Resolution**: Detects and resolves ambiguities in user queries.
- **Coreference Resolution**: Handles pronouns and references in follow-up questions.
- **Interactive User Prompts**: Asks for clarification when necessary.

## **Prerequisites**

- **Python 3.8 or higher**
- **Microsoft SQL Server instance** (local or remote)
- **ODBC Driver 17 for SQL Server**
- **GPU**: Recommended for running LLaMA models

## **Installation**

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/text-to-sql-project.git
   cd text-to-sql-project
