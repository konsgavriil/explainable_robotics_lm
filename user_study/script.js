document.addEventListener('DOMContentLoaded', function () {
    timestampIndex = 0;
    var content = $('#instructionBody');
    var trigger = $('#collapseTrigger');
    var closingBody = $('#ClosingBody');
    var video = document.getElementById('video');
    var option1 = document.getElementById('option1'); 
    var option2 = document.getElementById('option2'); 
    var option3 = document.getElementById('option3');
    var question = document.querySelector('.question p');
    var questions = ["Why does Alpha urgently return back to its starting point?"];
    var options1 = ["Low battery"];
    var options2 = ["Vehicle error"];
    var options3 = ["Bad weather"];
    const track = document.querySelector("track");
    const randomIndex = Math.floor(Math.random() * 2);
    const overlay = document.getElementById('overlay');
    const questionButton = document.getElementById('questionButton');
    const messageContainer = document.getElementById('messageContainer');
    const questionContainer = document.getElementById('questionContainer');
    const scenarios_a = ["videos/m34_alpha_a.webm", "videos/s1_alpha_a.webm", "videos/s4_delta_a.webm"];
    const scenarios_b = ["videos/m34_alpha_b.webm", "videos/s1_alpha_b.webm", "videos/s4_delta_b.webm"];
    const substrings = ["m34_alpha_a", "m34_alpha_b", "s1_alpha_a", "s1_alpha_b", "s4_delta_a", "s4_delta_b"];
    var scenarioTimestamps = [41];

    let videos;
    if (randomIndex === 0) {
        videos = scenarios_a;
    } else {
        videos = scenarios_b;
    }

    closingBody.hide();
    content.hide();


    $('.collapse-text').text('(Click to expand)');
    trigger.click(function () {
        content.toggle();
        var isVisible = content.is(':visible');
        if (isVisible) {
            $('.collapse-text').text('(Click to collapse)');
        } else {
            $('.collapse-text').text('(Click to expand)');
        }
    });

    messageContainer.addEventListener('click', function () {
        if (videos.length === 0) {
            messageContainer.style.display = 'none';
            $('#exampleBody').hide();
            closingBody.show();
            closingBody.focus();
        }
        messageContainer.style.display = 'none';
        video.controls = true;
        playRandomVideo();
    });

    video.addEventListener('ended', function () {
        if (videos.length === 0) {
            const heading = document.querySelector('.message h2');
            const paragraph = document.querySelector('.message p');
            heading.textContent = "You have reached the end of this section.";
            paragraph.textContent = "Click on the screen to continue to the closing questions.";
        }
        messageContainer.style.display = 'block';
        video.controls = false;
    });

    video.addEventListener('loadedmetadata', function () {
        const track = video.textTracks[0];
        track.mode = 'showing';
    });

    // Listen for timeupdate event to check for the timestamp
    video.addEventListener('timeupdate', function () {
        if (scenarioTimestamps.length === 0) {
            timestamp = 10000000000;
        } else {
            timestamp = scenarioTimestamps[timestampIndex];
            option1.textContent = options1[timestampIndex];
            option2.textContent = options2[timestampIndex];
            option3.textContent = options3[timestampIndex];
            question.textContent = questions[timestampIndex];
            option1.value = options1[timestampIndex];
            option2.value = options2[timestampIndex];
            option3.value = options3[timestampIndex];
            question.value = questions[timestampIndex];
        }

        if (video.currentTime >= timestamp) {
            video.pause();
            video.controls = false;
            questionContainer.style.display = 'block';
            scenarioTimestamps.splice(timestampIndex, 1);
            options1.splice(timestampIndex, 1);
            options2.splice(timestampIndex, 1);
            options3.splice(timestampIndex, 1);
            questions.splice(timestampIndex, 1);
        }
    });

    questionButton.addEventListener('click', function () {
        questionContainer.style.display = 'none';
        video.controls = true;
        video.play();
    });

    function playRandomVideo() {
        // Generate a random index within the range of the videoList array length
        const randomIndex = Math.floor(Math.random() * videos.length);
        // Get the selected video URL
        const selectedVideo = videos[randomIndex];

        let scenario = findSubstringInList(selectedVideo, substrings);

        switch (scenario) {
            case "s1_alpha_a":
                scenarioTimestamps = [7, 18, 34];
                track.src = "subtitles/s1_alpha/s1_alpha_causal_a.vtt";
                questions = ['s1_alpha_a_q1', 's1_alpha_a_q2', 's1_alpha_a_q3'];
                options1 = ['s1_alpha_a_q1o1', 's1_alpha_a_q1o2', 's1_alpha_a_q1o3'];
                options2 = ['s1_alpha_a_q2o1', 's1_alpha_a_q2o2', 's1_alpha_a_q2o3'];
                options3 = ['s1_alpha_a_q2o1', 's1_alpha_a_q2o2', 's1_alpha_a_q2o3'];
                break;
            case "s1_alpha_b":
                scenarioTimestamps = [8, 22, 52];
                track.src = "subtitles/s1_alpha/s1_alpha_causal_b.vtt";
                questions = ['s1_alpha_b_q1', 's1_alpha_b_q2', 's1_alpha_b_q3'];
                options1 = ['s1_alpha_b_q1o1', 's1_alpha_b_q1o2', 's1_alpha_b_q1o3'];
                options2 = ['s1_alpha_b_q2o1', 's1_alpha_b_q2o2', 's1_alpha_b_q2o3'];
                options3 = ['s1_alpha_b_q2o1', 's1_alpha_b_q2o2', 's1_alpha_b_q2o3'];
                break;
            case "s4_delta_a":
                scenarioTimestamps = [14, 50, 61];
                track.src = "subtitles/s4_delta/s4_delta_causal_a.vtt";
                questions = ['s4_delta_a_q1', 's4_delta_a_q2', 's4_delta_a_q3'];
                options1 = ['s4_delta_a_q1o1', 's4_delta_a_q1o2', 's4_delta_a_q1o3'];
                options2 = ['s4_delta_a_q2o1', 's4_delta_a_q2o2', 's4_delta_a_q2o3'];
                options3 = ['s4_delta_a_q2o1', 's4_delta_a_q2o2', 's4_delta_a_q2o3'];
                break;
            case "s4_delta_b":
                scenarioTimestamps = [14, 75, 88];
                track.src = "subtitles/s4_delta/s4_delta_causal_b.vtt";
                questions = ['s4_delta_b_q1', 's4_delta_b_q2', 's4_delta_b_q3'];
                options1 = ['s4_delta_b_q1o1', 's4_delta_b_q1o2', 's4_delta_b_q1o3'];
                options2 = ['s4_delta_b_q2o1', 's4_delta_b_q2o2', 's4_delta_b_q2o3'];
                options3 = ['s4_delta_b_q2o1', 's4_delta_b_q2o2', 's4_delta_b_q2o3'];
                break;
            case "m34_alpha_a":
                scenarioTimestamps = [32, 52, 85];
                track.src = "subtitles/m34_alpha/m34_alpha_causal_a.vtt";  
                questions = ['m34_alpha_a_q1', 'm34_alpha_a_q2', 'm34_alpha_a_q3'];
                options1 = ['m34_alpha_a_q1o1', 'm34_alpha_a_q1o2', 'm34_alpha_a_q1o3'];
                options2 = ['m34_alpha_a_q2o1', 'm34_alpha_a_q2o2', 'm34_alpha_a_q2o3'];
                options3 = ['m34_alpha_a_q2o1', 'm34_alpha_a_q2o2', 'm34_alpha_a_q2o3'];
                break;
            case "m34_alpha_b":
                scenarioTimestamps = [29, 48, 60];
                track.src = "subtitles/m34_alpha/m34_alpha_causal_b.vtt";         
                // questions = ['m34_alpha_b_q1', 'm34_alpha_b_q2', 'm34_alpha_b_q3'];
                // options1 = ['m34_alpha_b_q1o1', 'm34_alpha_b_q1o2', 'm34_alpha_b_q1o3'];
                // options2 = ['m34_alpha_b_q2o1', 'm34_alpha_b_q2o2', 'm34_alpha_b_q2o3'];
                // options3 = ['m34_alpha_b_q2o1', 'm34_alpha_b_q2o2', 'm34_alpha_b_q2o3'];
                questions = ['How did the vessels avoid a head on collision?', 'Why did the vessels decide to change loiter areas again?', 'What happened during the collision avoidance?'];
                options1 = ['Gilda reduced speed and Henry altered its trajectory', 'Henry reduced speed and Gilda altered its trajectory', 'Henry and Gilda moved in a clockwise direction to avoid each other'];
                options2 = ['Due to a time threshold allocated in their plan', 'Instructed by command and control', 'They replanned due to a change in the weather'];
                options3 = ['Gilda did not decelerate on time but collision was barely avoided', 'Gilda did not decelerate on time and there was a minor collision', 'Gilda decelerated on time and henry effectively changed its trajectory'];
                break;
            default:
                console.log("Unknown scenario.");
        }

        // Remove the selected video from the list
        videos.splice(randomIndex, 1);

        // Play the selected video
        playVideo(selectedVideo);
    }

    function playVideo(videoUrl) {
        video.src = videoUrl;
        video.play();
    }
});

function findSubstringInList(string, list) {
    for (let i = 0; i < list.length; i++) {
        if (string.includes(list[i])) {
            return list[i]; // Return the first substring found
        }
    }
    return null; // Return null if no substring is found in the list
}

