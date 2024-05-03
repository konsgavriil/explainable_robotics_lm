document.addEventListener('DOMContentLoaded', function () {
    var videoSequence = 0;
    var qTimestampIndex = 0;
    var eTimestampIndex = 0;
    var eScenarioTimestamps = [];
    var qScenarioTimestamps = [41];
    var content = $('#instructionBody');
    var trigger = $('#collapseTrigger');
    var closingBody = $('#ClosingBody');
    var video = document.getElementById('video');
    var option1 = document.getElementById('option1'); 
    var option2 = document.getElementById('option2'); 
    var option3 = document.getElementById('option3');
    var exp_option1 = document.getElementById('exp_option1');
    var exp_option2 = document.getElementById('exp_option2');
    var exp_option3 = document.getElementById('exp_option3');
    var question = document.querySelector('.question p');
    var questions = ["Why does Alpha urgently return back to its starting point?"];
    var options1 = ["Low battery"];
    var options2 = ["Vehicle error"];
    var options3 = ["Bad weather"];
    const track = document.querySelector("track");
    const randomIndex = Math.floor(Math.random() * 2);
    // const overlay = document.getElementById('overlay');
    const questionButton = document.getElementById('questionButton');
    const messageContainer = document.getElementById('messageContainer');
    const questionContainer = document.getElementById('questionContainer');
    const cfExplanationContainer = document.getElementById('cfExplanationContainer');
    const contrExplanationContainer = document.getElementById('contrExplanationContainer');
    const scenarios_a = ["videos/m34_alpha_a.webm", "videos/s1_alpha_a.webm", "videos/s4_delta_a.webm"];
    const scenarios_b = ["videos/m34_alpha_b.webm", "videos/s1_alpha_b.webm", "videos/s4_delta_b.webm"];
    const substrings = ["m34_alpha_a", "m34_alpha_b", "s1_alpha_a", "s1_alpha_b", "s4_delta_a", "s4_delta_b"];


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
        videoSequence++;
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
        if (qScenarioTimestamps.length === qTimestampIndex) {
            timestamp = 10000000000;
        } else {
            timestamp = qScenarioTimestamps[qTimestampIndex];
        }

        if (eScenarioTimestamps.length === eTimestampIndex) {
            etimestamp = 10000000000;
        } else {
            etimestamp = eScenarioTimestamps[eTimestampIndex];
        }

        if (video.currentTime >= timestamp) {
            option1.textContent = options1[qTimestampIndex];
            option2.textContent = options2[qTimestampIndex];
            option3.textContent = options3[qTimestampIndex];
            question.textContent = questions[qTimestampIndex];
            option1.value = options1[qTimestampIndex];
            option2.value = options2[qTimestampIndex];
            option3.value = options3[qTimestampIndex];
            question.value = questions[qTimestampIndex];
            video.pause();
            video.controls = false;
            questionContainer.style.display = 'block';
            qTimestampIndex++;
        } else if (video.currentTime >= etimestamp) {
            option1.textContent = options1[eTimestampIndex];
            option2.textContent = options2[eTimestampIndex];
            option3.textContent = options3[eTimestampIndex];
            question.textContent = questions[eTimestampIndex];
            option1.value = options1[eTimestampIndex];
            option2.value = options2[eTimestampIndex];
            option3.value = options3[eTimestampIndex];
            question.value = questions[eTimestampIndex];
            video.pause();
            video.controls = false;
            cfExplanationContainer.style.display = 'block';
            eTimestampIndex++;
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
        qTimestampIndex = 0;
        switch (scenario) {
            case "s1_alpha_a":
                qScenarioTimestamps = [7, 18, 34];
                track.src = "subtitles/s1_alpha/s1_alpha_causal_a.vtt";
                questions = ['How did Alpha decide to start with the mission', 'Which obstacles did Alpha avoid?', 'What is the obstacle proximity and which side does the vessel use to move around?'];
                options1 = ['Checked for dynamic obstacles and proceeded', 'A and B', 'close proximity and right side'];
                options2 = ['Pre-planned time', 'B and C', 'medium proximity and right side'];
                options3 = ['Deployed by command and control', 'C and E', 'medium proximity and left side'];
                eScenarioTimestamps = [4, 14, 28];
                cf_query1 = ["deploy=False, return = False", "obstacle_name = obstacle_a, obstacle_resolved = True", "obstacle_direction = Northwest, obstacle_proximity = medium"];
                cf_query2 = ["deploy=True, return = False", "obstacle_name = obstacle_b, obstacle_resolved = True", "obstacle_direction = Northeast, obstacle_proximity = medium"];
                cf_query3 = ["deploy=False, return = True", "obstacle_name = obstacle_c, obstacle_resolved = True", "obstacle_direction = Northwest, obstacle_proximity = nearby"];
                cf_explanation1 = ["If the vehicle is not deployed and does not return, then it stays idle waiting for a command.", "If the vehicle encounters obstacle A and resolves it, then it proceeds with the survey.", "If the vehicle encounters an obstacle in medium proximity to the northwest, then it moves to the right side to avoid it."];
                cf_explanation2 = ["If the vehicle is deployed and does not return, then it is executing a mission.", "If the vehicle encounters obstacle B and resolves it, then it proceeds with the survey.", "If the vehicle encounters an obstacle in medium proximity to the northeast, then it moves to the left side to avoid it."];
                cf_explanation3 = ["If the vehicle is not deployed and returns, then it is returning to its starting point.", "If the vehicle encounters obstacle C and resolves it, then it proceeds with the survey.", "If the vehicle encounters an obstacle in nearby proximity to the northwest, then there is no need to modify its trajectory."];
                contr_query1 = ["Why not return to the starting point?", "Why not avoid obstacle A?"];
                contr_query2 = ["Why not stay idle?", "Why not avoid obstacle B?"];
                contr_query3 = ["Why not avoid an obstacle?", "Why not avoid obstacle D?"];
                contr_explanation1 = ["Alpha would need to complete the survey or be asked to return by command and control.", "Alpha has not encountered obstacle A yet."];
                contr_explanation2 = ["Alpha would have returned to the starting point or cancel its deployment to stay idle.", "Alpha has not encountered obstacle B yet."];
                contr_explanation3 = ["The vessel needs to be in medium proximity to an obstacle to avoid it.", "There is no obstacle D in this mission."];
                break;
            case "s1_alpha_b":
                qScenarioTimestamps = [8, 22, 52];
                track.src = "subtitles/s1_alpha/s1_alpha_causal_b.vtt";
                questions = ['Where does the vessel move towards to?', 'What is the speed and depth of Alpha?', 'What is Alpha doing now?'];
                options1 = ['Point 0', 'Moderate speed and high depth', 'Returning after visiting its final waypoint'];
                options2 = ['Point 1', 'Moderate speed and depth', 'Going back due to low battery'];
                options3 = ['Point A', 'Very fast on surface', 'Going back due to weather conditions'];
                eScenarioTimestamps = [4, 17, 47];
                cf_query1 = ["deploy=True, return = False, next_point = point_0", "speed = moderate, depth = high", "deploy=False, return = False"];
                cf_query2 = ["deploy=True, return = False, next_point = point_1", "speed = moderate, depth = surface", "deploy=True, return = False"];
                cf_query3 = ["deploy=True, return = False, next_point = point_2", "speed = very fast, depth = surface", "deploy=False, return = True"];
                cf_explanation1 = ["Alpha is moving towards point 0 because it is the next waypoint in the survey.", "Alpha cannot move underwater since it's a surface vehicle.", "If the vehicle is not deployed and does not return, then it stays idle waiting for a command."];
                cf_explanation2 = ["Alpha is moving towards point 1 because it is the next waypoint in the survey.", "Alpha would need to start with the mission or return back to have a moderate speed.", "If the vehicle is deployed and does not return, then it is executing a mission."];
                cf_explanation3 = ["Alpha is moving towards point 2 because it is the next waypoint in the survey.", "Alpha would need to perform its survey to move very fast on the surface.", "If the vehicle returns, then it either completed the survey or was asked to return by command and control."];
                contr_query1 = ["Why not move towards point 1?", "Why not move underwater?", "Why not continue with the survey?"];
                contr_query2 = ["Why not move towards point A?", "Why not move with moderate speed?", "Why not stay idle?"];
                contr_query3 = ["Why not move towards point 8?", "Why not stay idle?", "Why not modify its trajectory?"];
                contr_explanation1 = ["The survey's initial waypoint is not point 1.", "Alpha cannot move underwater since it's a surface vehicle.", "Alpha has visited all survey waypoints."];
                contr_explanation2 = ["The survey's initial waypoint is not point A.", "Alpha would need to start with the mission or return back to have a moderate speed.", "Alpha has not reached its starting point."];
                contr_explanation3 = ["There is no point 8 in this mission.", "Alpha has not returned to its starting point yet.", "Alpha has not encountered an obstacle in medium proximity."];
                break;
            case "s4_delta_a":
                qScenarioTimestamps = [14, 50, 61];
                track.src = "subtitles/s4_delta/s4_delta_causal_a.vtt";
                questions = ['What is the speed and depth of the vessel?', 'Why is Delta moving back to the loiter area?', 'Why does Delta remain stationary?'];
                options1 = ['Low depth and moderate speed', 'Due to a time threshold', 'Reducing its depth'];
                options2 = ['High depth and moderate speed', 'It was asked by command and control', 'GPS Fix'];
                options3 = ['Moderate depth and fast speed', 'Visited all survey waypoints', 'Autonomy software error'];
                eScenarioTimestamps = [9, 40, 53];
                cf_query1 = ["depth = low, speed = low", "survey = true, survey_format = bowtie", "loiter = true, speed = idle"];
                cf_query2 = ["depth = very deep, speed = high", "survey = true, survey_format = lawnmower", "survey = true, speed = idle"];
                cf_query3 = ["depth = moderate, speed = idle", "survey = false, loiter = true", "return = true, speed = idle"];
                cf_explanation1 = ["Delta would need to be ascending to have this depth and speed.", "If delta is task to perform a bowtie survey, then it has to traverse all waypoints twice.", "If delta is loitering and is idle, then it is performing a GPS fix."];
                cf_explanation2 = ["Delta always maintains its depth to moderate. Also, it only moves in high speed when it is surveying or returning back.", "If delta is task to perform a lawnmower survey, then it has to traverse all waypoints once.", "If delta is surveying and is idle, then something upexpected occured."];
                cf_explanation3 = ["Delta would need to start performing a GPS fix to remain stationary.", "If delta is not surveying and is loitering, then it either completed the survey or was asked to loiter by command and control.", "If delta is returning and is idle, then it reached its starting point."];
                contr_query1 = ["Why not move at low depth and low speed?", ];
                contr_query2 = ["Why not move at high depth and moderate speed?",];
                contr_query3 = ["Why not move at high depth and stay idle?",];
                contr_explanation1 = ["Delta is not currently ascending. To ascend, it needs to stay idle and attempt a GPS fix during loiter.",];
                contr_explanation2 = ["The behaviour of Delta has been configured to avoid high depths. Also, instead of surveying or returning, it loiters around.",];
                contr_explanation3 = ["This is not a normal behaviour for Delta. If this behaviour is exhibited, it means that something unexperted has occured.",];
                break;
            case "s4_delta_b":
                qScenarioTimestamps = [14, 75, 88];
                track.src = "subtitles/s4_delta/s4_delta_causal_b.vtt";
                questions = ['What is the speed and depth of the vessel?', 'Why is Delta moving back to the loiter area?', 'Why does Delta remain stationary?'];
                options1 = ['Low depth and moderate speed', 'Due to a time threshold', 'Reducing its depth'];
                options2 = ['High depth and moderate speed', 'It was asked by command and control', 'GPS Fix'];
                options3 = ['Moderate depth and fast speed', 'Visited all survey waypoints', 'Autonomy software error'];
                eScenarioTimestamps = [9, 60, 80];
                cf_query1 = "";
                cf_query2 = "";
                cf_query3 = "";
                cf_explanation1 = "";
                cf_explanation2 = "";
                cf_explanation3 = "";
                contr_query1 = "";
                contr_query2 = "";
                contr_query3 = "";
                contr_explanation1 = "";
                contr_explanation2 = "";
                contr_explanation3 = "";
                break;
            case "m34_alpha_a":
                qScenarioTimestamps = [32, 52, 85];
                track.src = "subtitles/m34_alpha/m34_alpha_causal_a.vtt";  
                questions = ['What obstacle proximity causes the vessels to modify their trajectory?', 'Why do the vessel exhange loiter areas?', 'How did the vessels avoid a collision?'];
                options1 = ['Medium', 'Due to a planned patrol routine', 'Henry was waiting while Gilda maintained its course'];
                options2 = ['Close', 'Command and control request', 'Gilda was waiting while Henry maintained its course'];
                options3 = ['Very close', 'Time threshold', 'Both vessels reduced their speed and moved clockwise to avoid each other'];
                eScenarioTimestamps = [25, 45, 78];
                cf_query1 = "";
                cf_query2 = "";
                cf_query3 = "";
                cf_explanation1 = "";
                cf_explanation2 = "";
                cf_explanation3 = "";
                contr_query1 = "";
                contr_query2 = "";
                contr_query3 = "";
                contr_explanation1 = "";
                contr_explanation2 = "";
                contr_explanation3 = "";
                break;
            case "m34_alpha_b":
                qScenarioTimestamps = [29, 48, 60];
                track.src = "subtitles/m34_alpha/m34_alpha_causal_b.vtt";         
                questions = ['How did the vessels avoid a head on collision?', 'Why did the vessels decide to change loiter areas again?', 'What happened during the collision avoidance?'];
                options1 = ['Gilda reduced speed and Henry altered its trajectory', 'Due to a time threshold allocated in their plan', 'Gilda did not decelerate on time but collision was barely avoided'];
                options2 = ['Henry reduced speed and Gilda altered its trajectory', 'Instructed by command and control', 'Gilda did not decelerate on time and there was a minor collision'];
                options3 = ['Henry and Gilda moved in a clockwise direction to avoid each other', 'They replanned due to a change in the weather', 'Gilda decelerated on time and henry effectively changed its trajectory'];
                eScenarioTimestamps = [21, 41, 52];
                cf_query1 = "";
                cf_query2 = "";
                cf_query3 = "";
                cf_explanation1 = "";
                cf_explanation2 = "";
                cf_explanation3 = "";
                contr_query1 = "";
                contr_query2 = "";
                contr_query3 = "";
                contr_explanation1 = "";
                contr_explanation2 = "";
                contr_explanation3 = "";
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

