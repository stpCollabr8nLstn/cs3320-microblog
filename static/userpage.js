var followButtonStates = {
    'following': {
        text: 'Unfollow',
        action: 'destroy'
    },
    'self': {
        text: 'Yourself',
        disabled: true
    },
    'none': {
        text: 'Follow',
        highlighted: true,
        action: 'request'
    }
};

function setupButton(button) {
    /* set up this button! */
    var state = $(button).attr('data-state');
    console.log('button state: %s', state);
    /* get the info for the state */
    var config = followButtonStates[state];
    $(button).text(config.text);
    if (config.disabled) {
        $(button).attr('hidden', true);
    } else {
        $(button).removeAttr('hidden');
    }
    $(button).addClass(state);
    if (config.highlighted) {
        $(button).addClass('pure-button-primary');
    } else {
        $(button).removeClass('pure-button-primary');
    }
}

function onFollowClick() {
    var button = $(this);
    var state = $(this).attr('data-state');
    var action = followButtonStates[state].action;
    var url = '/follow/' + action;
    console.log('sending ajax call')
    $.ajax(url, {
        data: {
            init_id: authUserId,
            respond_id: parseInt($('#profile-shell').attr('data-user-id'), 10),
            _csrf_token: csrfToken
        },
        method: 'POST',
        success: function(response) {
            console.log('action %s succeeded', action);
            button.removeClass('pending');
            button.attr('data-state', response.new_state);
            setupButton(button);
        },
        error: function(err) {
            button.removeClass('pending');
            button.addClass('failed');
        }
    });
    console.log('pending');
    button.addClass('pending');
}

/* set up the subscribe button */
$('button.follow').each(function() {
    setupButton(this);
    $(this).on('click', onFollowClick)
});


function postMessage(content) {
    var button = $(this);
    if (button.attr('disabled')) return;

    var state = $(this).attr('data-state');
    $.ajax('/user/post', {
        data: {
            creator_id: authUserId,
            content: content,
            _csrf_token: csrfToken
        },
        method: 'POST',
        success: function(response) {
            button.removeClass('pending');
            alert('posted!');
        },
        error: function(err) {
            button.removeClass('pending');
            button.addClass('failed');
        }
    });
    button.addClass('pending');
}
$('button.new-post').on('click', postMessage);

/* Location tool */
if (navigator.geolocation) {
  console.log('Geolocation is supported!');
}
else {
  console.log('Geolocation is not supported for this Browser/OS version yet.');
}
