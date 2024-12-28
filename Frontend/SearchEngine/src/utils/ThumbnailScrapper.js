import axios from 'axios';
import * as cheerio from 'cheerio';

const fetchThumbnailFromAPI = async (url) => {
    try {
        const { data } = await axios.get(url);  // Fetch the HTML content of the article
        const $ = cheerio.load(data);  // Load the HTML content into cheerio

        // Scrape the image URL from the meta tag
        const imageUrl = $("meta[property='og:image']").attr("content");

        return imageUrl || 'https://via.placeholder.com/200';  // Return a fallback placeholder if no image is found
    } catch (error) {
        console.error('Error fetching image:', error);
        return 'https://via.placeholder.com/200';  // Return placeholder in case of error
    }
};

export { fetchThumbnailFromAPI };
