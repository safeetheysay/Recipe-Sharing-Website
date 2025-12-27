// Favorite button - AJAX request (Favorites Page Only)
$(document).on("click", ".favorite-btn", function (e) {
  e.preventDefault();
  const $this = $(this);
  const url = $this.attr("href");

  // Only run the remove logic if we're on the favorites page
  const isFavoritesPage = window.location.pathname.includes("my_favorites");
  const recipeCard = isFavoritesPage ? $this.closest(".recipe-card") : null;

  // Make AJAX request
  $.ajax({
    url: url,
    type: "GET",
    success: function (response) {
      // Toggle visual state based on server response
      if (response.favorited) {
        $this.addClass("favorited");
        $this.html("❤️ Favorited");
      } else {
        $this.removeClass("favorited");
        $this.html("♡ Favorite");

        // Only remove from DOM if we're on the favorites page
        if (isFavoritesPage && recipeCard) {
          recipeCard.remove();

          // Check if no recipes left and show empty message
          if ($(".recipe-card").length === 0) {
            $(".container").last().html(`
              <div class="text-center" style="background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 25px; padding: 20px; margin-bottom: 20px; color: #0c5460;">
                <h4>No Favorites Yet!</h4>
                <p>You haven't favorited any recipes yet. Start exploring and add some favorites!</p>
                <a href="/manage_recipes" class="btn btn-primary">Browse Recipes</a>
              </div>
            `);
          }
        }
      }
    },
    error: function () {
      alert("Error updating favorite status");
    },
  });
});

setTimeout(function () {
  const flashes = document.querySelectorAll(".alert");
  flashes.forEach((flash) => {
    flash.style.transition = "opacity 1s ease";
    flash.style.opacity = 0;
    setTimeout(() => flash.remove(), 1000); // remove from DOM after fade
  });
}, 2000);

// Comment form submission - FIXED VERSION
$(document).on("submit", '[id^="comment-form-"]', function (e) {
  e.preventDefault();
  console.log("✅ Comment form submitted");

  const form = $(this);
  const recipeId = form.attr("id").split("-")[2];
  const commentText = form.find('textarea[name="comment_text"]').val();
  console.log("Recipe ID:", recipeId, "Comment:", commentText);

  if (!commentText.trim()) {
    alert("Please enter a comment");
    return;
  }

  $.ajax({
    url: "/recipe/" + recipeId + "/comments",
    type: "POST",
    data: {
      comment_text: commentText,
    },
    success: function (response) {
      console.log("✅ Comment posted successfully");

      // FIXED: Only remove the "No comments" message, not all comments
      if ($("#comments-list-" + recipeId + " .text-muted").length) {
        $("#comments-list-" + recipeId + " .text-muted").remove();
      }

      // Add new comment at the BOTTOM (chronological order)
      $("#comments-list-" + recipeId).append(
        '<div class="comment" style="border-bottom: 1px solid #eee; padding: 10px 0; display: flex; justify-content: space-between; align-items: flex-start;">' +
          '<div style="flex: 1;">' +
          "<strong>" +
          response.username +
          "</strong>" +
          '<small class="text-muted">Just now</small>' +
          "<p>" +
          commentText +
          "</p>" +
          "</div>" +
          '<button class="btn btn-border-primary btn-xs delete-comment-btn" ' +
          'data-comment-id="' +
          response.comment_id +
          '" ' +
          'style="margin-left: 15px; padding: 4px 8px;">🗑️</button>' +
          "</div>"
      );

      // Scroll to the bottom to show the new comment
      var commentsContainer = $("#comments-list-" + recipeId);
      commentsContainer.scrollTop(commentsContainer[0].scrollHeight);

      // Clear textarea
      form.find("textarea").val("");

      // Update comment count
      var currentCount =
        parseInt(
          $('[data-target="#commentsModal-' + recipeId + '"]')
            .text()
            .match(/\d+/)[0]
        ) || 0;
      $('[data-target="#commentsModal-' + recipeId + '"]').text(
        "💬 Comments (" + (currentCount + 1) + ")"
      );

      console.log("✅ Comment added to list, all comments preserved");
    },
    error: function (xhr, status, error) {
      console.log("❌ POST Error:", error, "Status:", status);
      console.log("Response:", xhr.responseText);
      alert("Failed to post comment. Please try again.");
    },
  });
});

// Alternative: Reload on pageshow event (for back/forward navigation)
window.addEventListener("pageshow", function (event) {
  if (
    event.persisted ||
    (window.performance && window.performance.navigation.type === 2)
  ) {
    location.reload();
  }
});

setTimeout(function () {
  const flashes = document.querySelectorAll(".alert");
  flashes.forEach((flash) => {
    flash.style.transition = "opacity 1s ease";
    flash.style.opacity = 0;
    setTimeout(() => flash.remove(), 1000);
  });
}, 2000);

// Delete comment functionality - FIXED VERSION
$(document).on("click", ".delete-comment-btn", function (e) {
  e.preventDefault();
  e.stopPropagation(); // Prevent event bubbling

  const commentId = $(this).data("comment-id");
  const commentElement = $(this).closest(".comment");
  console.log("🗑️ Delete comment clicked:", commentId);

  if (confirm("Are you sure you want to delete this comment?")) {
    $.ajax({
      url: "/delete_comment/" + commentId,
      type: "POST",
      success: function (response) {
        console.log("✅ Delete response:", response);
        if (response.success) {
          // Remove the comment from the UI
          commentElement.remove();

          // Update comment count
          const recipeId = response.recipe_id;
          updateCommentCount(recipeId, -1);

          // If no comments left, show "No comments" message
          if (
            $("#comments-list-" + recipeId).children(".comment").length === 0
          ) {
            $("#comments-list-" + recipeId).html(
              '<p class="text-muted">No comments yet. Be the first to comment!</p>'
            );
          }

          // Show success message
          showFlashMessage("✅ Comment deleted successfully!", "success");
        } else {
          alert("Failed to delete comment: " + response.error);
        }
      },
      error: function (xhr, status, error) {
        console.log("❌ Delete error:", error, "Status:", status);
        console.log("Response:", xhr.responseText);
        alert("Failed to delete comment. Please try again.");
      },
    });
  }
});

// Helper function to update comment count
function updateCommentCount(recipeId, change) {
  const commentButton = $('[data-target="#commentsModal-' + recipeId + '"]');
  if (commentButton.length) {
    const currentText = commentButton.text();
    const match = currentText.match(/\((\d+)\)/);
    let currentCount = match ? parseInt(match[1]) : 0;
    currentCount = Math.max(0, currentCount + change);

    commentButton.text("💬 Comments (" + currentCount + ")");
  }
}

// Helper function to show flash messages
function showFlashMessage(message, type) {
  const alertClass = type === "success" ? "alert-success" : "alert-danger";
  const flashHtml = `
    <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="close" data-dismiss="alert">
        &times;
      </button>
    </div>
  `;

  $(".container").first().prepend(flashHtml);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    $(".alert").alert("close");
  }, 3000);
}
// Profile Picture Functions - WITH NULL CHECKS (SAFE FOR ALL PAGES)
function triggerFileInput() {
  const fileInput = document.getElementById("profile-pic-input");
  if (fileInput) {
    fileInput.click();
  }
}

// Show preview when image is selected - WITH NULL CHECK
const profilePicInput = document.getElementById("profile-pic-input");
if (profilePicInput) {
  profilePicInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const preview = document.getElementById("profile-preview");
        const noImageText = document.getElementById("no-image-text");
        const noImageBox = document.getElementById("no-image-box");

        // Update preview image
        if (preview) {
          preview.src = e.target.result;
          preview.style.display = "block";
          preview.style.border = "3px solid #007bff";
        }

        // Hide "No Image" elements
        if (noImageText) noImageText.style.display = "none";
        if (noImageBox) {
          noImageBox.style.background = "transparent";
          noImageBox.style.border = "none";
        }
      };
      reader.readAsDataURL(file);

      // Show confirm/cancel buttons, hide change button
      const changeBtn = document.getElementById("change-btn");
      const confirmBtn = document.getElementById("confirm-picture");
      const cancelBtn = document.getElementById("cancel-picture");
      const removeBtn = document.getElementById("remove-btn");

      if (changeBtn) changeBtn.style.display = "none";
      if (confirmBtn) confirmBtn.style.display = "inline-block";
      if (cancelBtn) cancelBtn.style.display = "inline-block";
      if (removeBtn) removeBtn.style.display = "none";
    }
  });
}

// Cancel picture selection - WITH NULL CHECK
const cancelPictureBtn = document.getElementById("cancel-picture");
if (cancelPictureBtn) {
  cancelPictureBtn.addEventListener("click", function () {
    // Reset file input
    const fileInput = document.getElementById("profile-pic-input");
    if (fileInput) fileInput.value = "";

    const preview = document.getElementById("profile-preview");
    const noImageText = document.getElementById("no-image-text");
    const noImageBox = document.getElementById("no-image-box");

    // Get original state from data attributes
    const hasOriginalImage =
      document.body.getAttribute("data-has-image") === "true";
    const originalImageSrc = document.body.getAttribute("data-original-image");

    if (hasOriginalImage && originalImageSrc && preview) {
      // If had image originally
      preview.src = originalImageSrc;
      preview.style.display = "block";
      preview.style.border = "3px solid #007bff";
      if (noImageBox) {
        noImageBox.style.background = "transparent";
        noImageBox.style.border = "none";
      }
    } else {
      // If no image originally
      if (preview) {
        preview.style.display = "none";
        preview.style.border = "none";
      }
      if (noImageText) noImageText.style.display = "block";
      if (noImageBox) {
        noImageBox.style.background = "#e9ecef";
        noImageBox.style.border = "2px dashed #ccc";
      }
    }

    // Reset buttons
    const changeBtn = document.getElementById("change-btn");
    const confirmBtn = document.getElementById("confirm-picture");
    const cancelBtn = document.getElementById("cancel-picture");
    const removeBtn = document.getElementById("remove-btn");

    if (changeBtn) changeBtn.style.display = "inline-block";
    if (confirmBtn) confirmBtn.style.display = "none";
    if (cancelBtn) cancelBtn.style.display = "none";
    if (removeBtn) removeBtn.style.display = "inline-block";
  });
}

// Remove profile picture - WITH NULL CHECK
function removeProfilePicture() {
  if (confirm("Are you sure you want to remove your profile picture?")) {
    const removeForm = document.getElementById("remove-picture-form");
    if (removeForm) {
      removeForm.submit();
    }
  }
}

// SEARCH FUNCTIONALITY - FIXED VERSION
let searchInitialized = false;

function initializeSearch() {
  if (searchInitialized) return;

  const $searchToggle = $("#search-toggle");
  const $searchForm = $("#search-form");

  if ($searchToggle.length && $searchForm.length) {
    // Remove any existing handlers
    $searchToggle.off("click");
    $(document).off("click.search");
    $searchForm.off("click");

    // Set initial state
    $searchForm.hide();

    // Add new handlers
    $searchToggle.on("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      $searchForm.toggle("fast");
    });

    // Close when clicking outside
    $(document).on("click.search", function (event) {
      if (!$(event.target).closest(".search-container").length) {
        $searchForm.hide();
      }
    });

    // Prevent form from closing when clicking inside
    $searchForm.on("click", function (e) {
      e.stopPropagation();
    });

    searchInitialized = true;
    console.log("✅ Search initialized");
  }
}

setTimeout(function () {
  const flashes = document.querySelectorAll(".alert");
  flashes.forEach((flash) => {
    flash.style.transition = "opacity 1s ease";
    flash.style.opacity = 0;
    setTimeout(() => flash.remove(), 1000); // remove from DOM after fade
  });
}, 2000);

function enableEditing(field) {
  // Hide all other edit sections first
  cancelEditing("username");
  cancelEditing("email");
  cancelEditing("phone");
  cancelEditing("cnic");
  cancelEditing("password");

  // Show the selected edit section
  document.getElementById(field + "-display").style.display = "none";
  document.getElementById(field + "-edit").style.display = "block";
}

function cancelEditing(field) {
  document.getElementById(field + "-display").style.display = "block";
  document.getElementById(field + "-edit").style.display = "none";
}
// Check for new notifications every 30 seconds
function checkNotifications() {
  console.log("🔔 Checking notifications..."); // ADD THIS FOR DEBUGGING

  $.ajax({
    url: "/get_notifications",
    type: "GET",
    success: function (response) {
      console.log("✅ Notifications received:", response); // ADD THIS
      updateNotificationUI(response.notifications, response.unread_count);
    },
    error: function (xhr, status, error) {
      console.log("❌ Notifications error:", error);
      console.log("Response:", xhr.responseText);
    },
  });
}

// Update notification UI
function updateNotificationUI(notifications, unreadCount) {
  console.log("🔄 Updating UI with:", unreadCount, "unread notifications");

  // Update badge count
  const notificationCount = document.getElementById("notification-count");
  if (notificationCount) {
    notificationCount.textContent = unreadCount;
    console.log("✅ Badge updated to:", unreadCount);
  } else {
    console.log("❌ notification-count element not found");
  }

  // Update dropdown list
  const list = document.getElementById("notifications-list");
  if (list) {
    list.innerHTML = "";

    if (notifications.length === 0) {
      list.innerHTML = '<li class="dropdown-header">No new notifications</li>';
      console.log("ℹ️ No notifications to display");
    } else {
      notifications.forEach((notif) => {
        list.innerHTML += `
          <li class="${notif.is_read ? "" : "unread"}">
            <a href="/view_recipe/${notif.recipe_id}#comment-${
          notif.comment_id
        }">
              ${notif.message.replace(/\n/g, "<br>")}
            </a>
          </li>
        `;
      });

      // DYNAMIC COLOR CODING - Add this part
      const notificationLinks = list.querySelectorAll("a");
      notificationLinks.forEach((link) => {
        link.style.whiteSpace = "normal";
        link.style.wordWrap = "break-word";
        link.style.maxWidth = "300px";
        link.style.padding = "10px 15px";
        link.style.lineHeight = "1.4";

        // Remove the default border-left from CSS
        link.style.borderLeft = "none";

        // Dynamic color coding based on content
        const message = link.textContent.toLowerCase();
        if (message.includes("password")) {
          link.style.borderLeft = "4px solid #4100b9ff"; // Purple for password
        } else if (message.includes("comment")) {
          link.style.borderLeft = "4px solid #ffa600ff"; // Blue for comments
        } else if (message.includes("approved")) {
          link.style.borderLeft = "4px solid #28a745"; // Green for approvals
        } else if (message.includes("rejected")) {
          link.style.borderLeft = "4px solid #dc3545"; // Red for rejections
        } else if (message.includes("favorite")) {
          link.style.borderLeft = "4px solid #fd7e14"; // Orange for favorites
        } else {
          link.style.borderLeft = "4px solid #17a2b8"; // Cyan for others
        }
      });

      console.log("✅ Displaying", notifications.length, "notifications");
    }
  } else {
    console.log("❌ notifications-list element not found");
  }
}
// FIX FOR MODAL BLINKING - SINGLE EVENT HANDLER WITH PROPER PREVENTION
let modalHandlerInitialized = false;

function initializeModalHandlers() {
  if (modalHandlerInitialized) return;

  $(document)
    .off("click.modalFix")
    .on("click.modalFix", '[data-target^="#commentsModal-"]', function (e) {
      e.preventDefault();
      e.stopImmediatePropagation();

      const targetModal = $(this).data("target");
      console.log("Opening modal:", targetModal);

      // Simply show the modal without complex initialization
      $(targetModal).modal("show");

      return false;
    });

  modalHandlerInitialized = true;
  console.log("✅ Modal handlers initialized");
}

// MOVE AUTO-CHECK INSIDE document.ready
$(document).ready(function () {
  // INITIALIZE SEARCH - FIXED
  initializeSearch();

  // INITIALIZE MODAL HANDLERS - ADD THIS
  initializeModalHandlers();

  // AUTO-START NOTIFICATIONS - MOVED HERE
  if (document.getElementById("notification-count")) {
    console.log("🚀 Starting notification system...");
    checkNotifications(); // Initial check

    // Check every 30 seconds
    setInterval(checkNotifications, 30000);
  } else {
    console.log("ℹ️ No notification elements found on this page");
  }
});
