document.getElementById("show-news").addEventListener("click", function (e) {
    e.preventDefault();

    const container = document.getElementById("news-container");
    container.style.display = container.style.display === "none" ? "block" : "none";

    const topic = document.getElementById("topic").value;
    fetch("/fetch_and_store?q=" + encodeURIComponent(topic))
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("news-container");
            const template = document.getElementById("article-template");
            container.innerHTML = ""; // Clear existing articles

            data.articles.forEach(article => {
                const clone = document.importNode(template.content, true);
                const articleElement = clone.querySelector("article");

                // Set the link text and href
                const link = articleElement.querySelector("a");
                link.href = article.url;
                link.textContent = article.title;

                // Set the content
                const content = articleElement.querySelector("p");
                content.textContent = article.content;

                function formatTimeAgo(dateString) {
                    const publishedDate = new Date(dateString);
                    const now = new Date();
                    const diffInSeconds = Math.floor((now - publishedDate) / 1000);

                    if (diffInSeconds < 60) {
                        return `${diffInSeconds} seconds ago`;
                    } else if (diffInSeconds < 3600) {
                        return `${Math.floor(diffInSeconds / 60)} minutes ago`;
                    } else if (diffInSeconds < 86400) {
                        return `${Math.floor(diffInSeconds / 3600)} hours ago`;
                    } else if (diffInSeconds < 2592000) { // 30 days
                        return `${Math.floor(diffInSeconds / 86400)} days ago`;
                    } else if (diffInSeconds < 31536000) { // 12 months
                        return `${Math.floor(diffInSeconds / 2592000)} months ago`;
                    } else {
                        return `${Math.floor(diffInSeconds / 31536000)} years ago`;
                    }
                }

                // Usage
                const timeElement = document.createElement("small");
                timeElement.classList.add("text-muted", "d-block", "mt-1");
                timeElement.textContent = `Published: ${formatTimeAgo(article.published_at)}`;
                articleElement.appendChild(timeElement);

                container.appendChild(clone);
            });
        });

});
