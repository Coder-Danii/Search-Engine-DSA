// import axios from 'axios';
// import * as cheerio from 'cheerio';
// import cors from 'cors';
// import express from 'express';

// const app = express();

// // Enable CORS
// app.use(cors());

// // Middleware to parse JSON requests
// app.use(express.json());

// // Function to scrape the thumbnail image
// const scrapeThumbnailImage = async (url) => {
//     try {
//         // Fetch the HTML content from the URL
//         const { data } = await axios.get(url);

//         // Load the HTML content into cheerio
//         const $ = cheerio.load(data);

//         // Extract the image URL from the meta tag with property "og:image"
//         const imageUrl = $("meta[property='og:image']").attr("content");

//         // If no image URL found, return a placeholder
//         return imageUrl || 'https://via.placeholder.com/200';
//     } catch (error) {
//         console.error('Error fetching the image:', error);
//         return 'https://via.placeholder.com/200'; // Return a placeholder image in case of error
//     }
// };

// // Test route
// app.get('/', async (req, res) => {
//     res.send('Reached');
// });

// // Endpoint to scrape images for a list of URLs
// app.post('/scrape-images', async (req, res) => {
//     const urls = req.body.urls;
//     console.log("POST /scrape-images reached with URLs:", urls);

//     if (!urls || !Array.isArray(urls)) {
//         return res.status(400).json({ error: 'URLs are required and should be an array.' });
//     }

//     try {
//         const imageUrls = [];
//         for (let url of urls) {
//             const imageUrl = await scrapeThumbnailImage(url);
//             imageUrls.push({ url, image: imageUrl });
//         }

//         // Respond with the scraped images
//         res.json({ imageUrls });
//     } catch (error) {
//         console.error('Error scraping images:', error);
//         res.status(500).json({ error: 'Failed to scrape images' });
//     }
// });

// const port = 5000;
// app.listen(port, () => {
//     console.log(`Server is running at http://localhost:${port}`);
// });
