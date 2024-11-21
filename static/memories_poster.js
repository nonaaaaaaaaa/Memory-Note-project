document.addEventListener('DOMContentLoaded', async (event) => {
    event.preventDefault();

    const body = document.querySelector('body');
    const script = document.querySelector('script');
    const section = document.createElement('section');

    section.className = 'memories_container';
    body.insertBefore(section, script);

    try {
        const response = await fetch('/api/get-memories', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        });

        const data = await response.json();

        for (const memory of data) {
            const [
                memory_card_div,
                memory_header_div,
                memory_content_div,
                memory_footer_div
            ] = Array.from({length: 4}, () => document.createElement('div'));

            const images = Array.isArray(memory.image) ? memory.image : [];
            const imagesElements = images.map(imgUrl => `
                <div class="memory-image">
                    <img src="${imgUrl}" alt="Memory Image" class="memory-image">
                </div>
            `).join('');

            memory_card_div.className = 'memory-card';
            memory_card_div.id = memory['id'];

            memory_header_div.className = 'memory-header';

            // Fetch user data synchronously using async/await
            const userResponse = await fetch(`/api/users/${memory['user_id']}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            });

            const currentUserResponse = await fetch(`/api/current-user`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            });

            const user = await userResponse.json();
            const current_user = await currentUserResponse.json();
            const liked_list = current_user['memories']['liked'];

            memory_header_div.innerHTML = `
                <img src="${user['image']}" alt="Profile Image" class="profile-img">
                <div class="user-info">
                    <h3 class="username">${user['username']}</h3>
                    <p class="memory-date">${memory['timestamp']}</p>
                </div>
            `;

            memory_card_div.appendChild(memory_header_div);

            memory_content_div.className = 'memory-content';
            memory_content_div.innerHTML = `
                <p>${memory['description']}</p>
                <div class="memory-images" style="${images.length === 0 ? 'display: none;' : ''}">
                    ${imagesElements}
                </div>
            `;

            memory_card_div.appendChild(memory_content_div);

            let like_memory = liked_list.includes(memory['id']);

            memory_footer_div.className = 'memory-footer';
            memory_footer_div.innerHTML = `
                <button class="action-button like-button" style="${like_memory ? 'background-color: rgb(220, 53, 69);' : ''}">
                    <i class="fas fa-heart"></i> ${memory['likes'] > 0 ? memory['likes'] : 'Like'}
                </button>
                <button class="action-button comment-button">
                    <i class="fas fa-comment-dots"></i> Comment
                </button>
                <button class="action-button share-button">
                    <i class="fas fa-share-alt"></i> Share
                </button>
            `;

            memory_card_div.appendChild(memory_footer_div);

            const likeButton = memory_footer_div.querySelector('.like-button');
            likeButton.addEventListener('click', async function(event) {
                event.preventDefault();

                // Update like_memory state and button appearance
                like_memory = !like_memory;
                likeButton.style.backgroundColor = like_memory ? 'rgb(220, 53, 69)' : '';

                // Update likes count based on like_memory state
                memory['likes'] = like_memory ? memory['likes'] + 1 : memory['likes'] - 1;
                likeButton.innerHTML = `
                    <i class="fas fa-heart"></i> ${memory['likes'] > 0 ? memory['likes'] : 'Like'}
                `;
                // Handle the like button click event here
                try {
                    const response = await fetch(`/api/users/like/${memory_card_div.id}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }
                    });

                    const result = await response.json();

                    if (!response.ok && result.message !== 'true') {
                        console.error('Error liking memory:', result.error);
                    }
                } catch (error) {
                    console.error('An error occurred:', error);
                }
            });

            async function renderComments(comments) {
                const commentsElements = await Promise.all(comments.map(async (comment) => {
                    const userData = await fetchUserData(comment['user_id']); // Fetch user data
                    console.log(userData['image']);
                    
                    return `
                        <div class="comment-item">
                            <img class="commenter-img" src="${userData ? userData['image'] : ''}" alt="Commenter Image">
                            <div class="comment-content">
                                <h5>${userData ? userData['username'] : 'Unknown User'}</h5>
                                <h6>${comment['timestamp']}</h6>
                                <p>${comment['comment']}</p>
                            </div>
                        </div>
                    `;
                }));

                return commentsElements.join('');
            }

            // Usage
            const comments = Array.isArray(memory['comments']) ? memory['comments'] : [];
            const commentsElements = await renderComments(comments);

            // Create and append the comment modal
            const comment_div = document.createElement('div');
            comment_div.className = 'comment_modal';
            comment_div.id = `commentsModal_${memory['id']}`;
            comment_div.innerHTML = `
                <div class="modal-content-comment">
                    <span class="close-button-comment">&times;</span>
                    <h2>Comments</h2>
                    <input class="commentInput" id="commentInput_${memory['id']}" name="commentInput" placeholder="What's your Comment?">
                    <div id="commentsList_${memory['id']}" class="comments-list">
                        ${commentsElements}
                    </div>
                </div>
            `;

            section.appendChild(comment_div);

            const commentButton = memory_card_div.querySelector('.comment-button');
            commentButton.addEventListener('click', async function(event) {
                event.preventDefault();
                // Open the comment modal specific to this memory
                const commentModal = document.getElementById(`commentsModal_${memory['id']}`);
                commentModal.style.display = 'block';
                commentButton.style.backgroundColor = 'rgb(40, 167, 69)';
            });

            const closeButton = comment_div.querySelector('.close-button-comment');
            closeButton.addEventListener('click', function() {
                const commentModal = document.getElementById(`commentsModal_${memory['id']}`);
                commentModal.style.display = 'none';
                commentButton.style.backgroundColor = 'rgb(33, 33, 33)';
            });

            // Close modal when clicking outside of it
            window.addEventListener('click', (event) => {
                const commentModal = document.getElementById(`commentsModal_${memory['id']}`);
                if (event.target === commentModal) {
                    commentModal.style.display = 'none';
                    commentButton.style.backgroundColor = 'rgb(33, 33, 33)';
                }
            });

            section.appendChild(memory_card_div);
        }
    } catch (error) {
        console.error('Error:', error);
    }

    async function fetchUserData(userId) {
        try {
            const response = await fetch(`/api/users/${userId}`);
            const userData = await response.json();
            return userData;
        } catch (error) {
            console.error('Error fetching user data:', error);
            return null; // Handle error case
        }
    }
});