export function ArticleList({ articles }) {
    // Extract the array from the `searchResults` property
    console.log(articles)
    const articleArray = articles || [];

    if (!Array.isArray(articleArray)) {
        console.error("Expected 'searchResults' to be an array, but got:", articleArray);
        return null;
    }

    return (
        <div className="space-y-6">
            {articleArray.length === 0 ? (
                <p className="text-center text-brown-500 dark:text-beige-200">No articles found.</p>
            ) : (
                articleArray.map((article) => (
                    <article
                        key={typeof article.doc_id === 'object' ? JSON.stringify(article.doc_id) : article.doc_id}
                        className="flex gap-6 p-4 bg-white dark:bg-brown-800 rounded-lg shadow-md border-2 border-brown-700 dark:border-beige-300"
                    >
                        <img
                            src="/medium-logo.png" // Medium logo for all articles
                            alt="Medium logo"
                            className="w-32 h-24 object-contain rounded-lg" // Reduced dimensions
                        />
                        <div className="flex flex-col flex-1">
                            <h2 className="text-xl font-bold text-brown-800 dark:text-beige-100 mb-2">
                                <a
                                    href={
                                        typeof article.url === 'object'
                                            ? JSON.stringify(article.url)
                                            : article.url || "#"
                                    }
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {typeof article.title === 'object' ? JSON.stringify(article.title) : article.title || "Untitled"}
                                </a>
                            </h2>

                            <p className="text-brown-600 dark:text-beige-300 mb-4 line-clamp-2">
                                {typeof article.text === 'object' ? JSON.stringify(article.text) : article.text || "No preview available"}
                            </p>
                            <div className="mt-auto">
                                <span className="text-sm text-brown-500 dark:text-beige-200">
                                    {typeof article.authors === 'object' ? JSON.stringify(article.author) : article.authors || "Unknown Author"}
                                </span>
                                <br />
                                <span className="text-sm text-grey-500 dark:text-grey-200">
                                    {typeof article.timestamp === 'object' ? JSON.stringify(article.timestamp) : article.timestamp || "No timestamp available"}
                                </span>
                            </div>
                        </div>
                    </article>
                ))


            )}
        </div>
    );
}
