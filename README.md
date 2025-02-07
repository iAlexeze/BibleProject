# EverydayBible App

The **EverydayBible App** is a simple Flask web application that allows users to access and read Bible scriptures. It uses the Bible API to fetch translations, books, chapters, and verses. The app also includes features like rate limiting, caching, and logging for efficient operation.

## Features
- **Fetch Bible Translations**: Get a list of available Bible translations.
- **Fetch Books**: Retrieve a list of books in a given translation.
- **Fetch Chapters**: Get available chapters in a book.
- **Read Scripture**: Retrieve and display specific verses from the Bible.
- **Rate Limiting**: Protects the app from excessive requests.
- **Caching**: Speeds up repeated requests.
- **Logging**: Detailed logs of request times and errors.

---

## Setup and Installation

### Prerequisites
1. **Python 3.7+**  
2. **pip** (Python package installer)

### Install Dependencies
Clone the repository and install the required Python dependencies.

```bash
git clone https://github.com/yourusername/everydaybible.git
cd everydaybible
pip install -r requirements.txt
```

### Set Up Environment Variables
The app uses an environment variable `PORT` to set the port for the Flask app. You can set it as follows:
```bash
export PORT=2323  # Or any other port you prefer
```

### Run the App
To run the app locally, simply execute the following command:

```bash
python main.py
```

The app will be available at `http://localhost:2323` (or the port you specified).

---

## Endpoints

### 1. **Homepage**
- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns the homepage of the app.

### 2. **Fetch Available Translations**
- **URL**: `/translations`
- **Method**: `GET`
- **Description**: Fetches all available Bible translations.
- **Example Response**:
  ```json
  ["KJV", "WEB", "NIV"]
  ```

### 3. **Fetch Books in a Translation**
- **URL**: `/books?translation=web`
- **Method**: `GET`
- **Description**: Fetches all the books in the given translation.
- **Query Parameters**:
  - `translation`: The Bible translation (default is `web`).
- **Example Response**:
  ```json
  ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
  ```

### 4. **Fetch Chapters of a Book**
- **URL**: `/chapters?book=Genesis&translation=web`
- **Method**: `GET`
- **Description**: Fetches the chapters of the specified book.
- **Query Parameters**:
  - `book`: Name of the book.
  - `translation`: Bible translation (default is `web`).
- **Example Response**:
  ```json
  [1, 2, 3, 4, 5, 6, 7, ...]
  ```

### 5. **Read Scripture (Verses)**
- **URL**: `/read?book=Genesis&chapter=1&translation=web`
- **Method**: `GET`
- **Description**: Fetches specific verses from a book and chapter.
- **Query Parameters**:
  - `book`: The book name.
  - `chapter`: The chapter number.
  - `translation`: Bible translation (default is `web`).
- **Example Response**:
  - This will render an HTML page displaying the verses from the specified chapter.

---

## Docker Support

You can deploy the app using Docker.

### Docker Setup
1. **Build the Docker image**:
   ```bash
   docker build -t everydaybible .
   ```
2. **Run the container**:
   ```bash
   docker run -e PORT=2323 -p 2323:5000 everydaybible
   ```
3. **Access the Application**:
    
You can access the application on http://localhost:2323

### Docker Compose Setup

If you prefer using **Docker Compose**, use the following commands:

1. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode**:
   ```bash
   docker-compose up -d
   ```

3. **Stop the containers**:
   ```bash
   docker-compose down
   ```
4. **Access the Application**:
    
You can access the application on http://localhost:2323. `2323` is the default port specified in the [compose.yml](compose.yml) file as shown:
   ```bash
    environment:
      - PORT=2323       # You can use any port number of your choice
    ports:
      - "2323:2323"
   ```

---

## Logging and Caching

- **Logging**: Logs are stored in `app.log` and also displayed in the terminal for easy debugging.
- **Caching**: A simple cache is used to limit the rate of requests and store recent data for faster responses.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---