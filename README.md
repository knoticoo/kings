# Canon ViaPrint 3200 Manager

A web application for managing paper types and cross-side corrections for Canon ViaPrint 3200 printers.

## Features

- **Paper Database**: Manage 20+ different paper types with specifications
- **Cross-side Corrections**: Save and quickly apply correction settings for each paper type
- **Quick Apply**: One-click application of saved settings
- **Search & Filter**: Find papers by weight, finish, or name
- **Persistent Storage**: Settings saved in browser storage

## Quick Start

### Option 1: Docker (Recommended)

1. **Make the deployment script executable:**
   ```bash
   chmod +x deploy.sh
   ```

2. **Deploy the application:**
   ```bash
   ./deploy.sh
   ```

3. **Access the app:**
   - Open your browser to `http://your-vps-ip:6000`

### Option 2: Manual Docker Compose

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Check status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

### Option 3: Direct Node.js (Development)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the server:**
   ```bash
   npm start
   ```

3. **Access the app:**
   - Open your browser to `http://localhost:6000`

## Configuration

### Environment Variables

- `PORT`: Server port (default: 6000)
- `NODE_ENV`: Environment (production/development)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS

### Port Configuration

The app runs on port 6000 by default to avoid conflicts with other applications like Next.js (which typically runs on port 3000).

## Usage

### Managing Papers

1. **View Papers**: All paper types are displayed in the main database view
2. **Search**: Use the search bar to find specific papers
3. **Filter**: Filter by weight or finish type
4. **Add New**: Click "Add Paper" to add new paper types

### Cross-side Corrections

1. **Quick Apply**: 
   - Select a paper type from the dropdown
   - Click "Apply Saved Settings" to instantly load saved corrections

2. **Manual Settings**:
   - Select a paper type
   - Enter correction values (Cross 1, 2, 3, 4)
   - Click "Save Settings" to store for future use

3. **Load Saved Settings**:
   - Select a paper type
   - Click "Load Saved Settings" to populate the form with saved values

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/papers` - Get all papers
- `POST /api/papers` - Add new paper
- `PUT /api/papers/:id/corrections` - Save corrections for paper

## File Structure

```
├── index.html          # Main HTML file
├── styles.css          # CSS styles
├── script.js           # Frontend JavaScript
├── server.js           # Express server
├── package.json        # Node.js dependencies
├── data/
│   └── papers.json     # Paper database
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── deploy.sh           # Deployment script
```

## Troubleshooting

### Port Already in Use

If port 6000 is already in use:

```bash
# Check what's using the port
lsof -i :6000

# Stop the existing service
docker-compose down
```

### Service Won't Start

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Check Docker status:**
   ```bash
   docker-compose ps
   ```

3. **Rebuild the container:**
   ```bash
   docker-compose up --build -d
   ```

### Data Persistence

Paper corrections are stored in the `data/` directory and persist between container restarts.

## Security

- The app uses Helmet.js for security headers
- CORS is configured to prevent conflicts with other apps
- Non-root user in Docker container
- Input validation and sanitization

## Support

For issues or questions, check the logs first:

```bash
docker-compose logs -f
```

## License

MIT License - feel free to modify and use as needed.