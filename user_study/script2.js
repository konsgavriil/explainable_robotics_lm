document.addEventListener('DOMContentLoaded', function () {
    var condition = -1;
    var conditions = [3, 1, 2];
    var content = $('#instructionBody');
    var trigger = $('#collapseTrigger');
    // var closingBody = $('#closingBody'); 
    var scenario1 = $('#scenario1Body'); 
    var scenario2 = $('#scenario2Body'); 
    var scenario3 = $('#scenario3Body'); 
    const scenario1Body = document.getElementById('scenario1Body');
    const scenario2Body = document.getElementById('scenario2Body');
    const scenario3Body = document.getElementById('scenario3Body');
    const answerButton1 = document.getElementById('answerButton1');
    const answerButton2 = document.getElementById('answerButton2');
    const answerButton3 = document.getElementById('answerButton3');
    answerButton1.disabled = true;
    answerButton2.disabled = true;
    answerButton3.disabled = true;

    const randomIndex = Math.floor(Math.random() * 2);
    const images_a = ['https://zenodo.org/records/11214735/files/causal2.png', 'https://zenodo.org/records/11214735/files/counterfactual2.png', 'https://zenodo.org/records/11214735/files/contrastive1.png'];
    const images_b = ['https://zenodo.org/records/11214735/files/causal1.png', 'https://zenodo.org/records/11214735/files/counterfactual1.png', 'https://zenodo.org/records/11214735/files/contrastive2.png'];
    const descriptions_a = ['Gilda was loitering on the right side and is about to exchange its loiter area with Henry. At the moment, the vessel is moving towards point 1 that is located southwest of it using the same heading. At the moment, Gilda is away from any obstacles or vessels and does not need to modify its trajectory for avoidance.', 'On its way towards a loiter area, Henry stops at a specific location to perform a GPS fix. This means that the longitude and latitude of the vessel is staying the same, but its depth is decreasing as the vessel is moving towards the surface to receive a signal. Which of the following explanations do you prefer for answering the corresponding query?', "Alpha is moving towards the final waypoint of the survey (point 2) while avoiding an obstacle. Once, the vessel has visited all waypoints, it has to return back to its starting point to be retrieved. The following query asks why the vessel hasn't already activated its return behaviour.Please select the explanation that best answers the question."];
    const descriptions_b = ['Henry is performing a survey in a bowtie pattern and is moving towards point 2 that is located northwest of the vessel. Select the explanation that best describes the current state of the autonomous underwater vehicle.', "After finishing its survey, Alpha is moving towards its starting point for pick up. If it's return is cancelled, then the vessel is programmed to restart its survey again.Select the explanation that best describes this alternative outcome.", 'In this scenario, Gilda avoids obstacles and contact collision simultaneously. The vessel is programmed to solve these unexpected outcomes using predefined protocols. However, these protocols do not include an immediate return towards the starting point, unless if instructed by command and control. Select the explanation that best justifies why the vessel is not returning back.'];
    const options1_a = ["Gilda is currently in the process of loitering fast towards point 1 with a southwest heading. Since there is a new loiter area available, Gilda's active behavior is influenced to continue loitering rather than returning to the starting point.Additionally, there is an obstacle at a very far distance and another vessel at a far distance, so there is no need for Gilda to avoid them.", 'The vessel has pinpointed its position and is now ready to continue its mission.', 'Alpha still needs to visit point 2 before returning back to its starting point.'];
    const options2_a = ['Gilda is in the process of exchanging loiter areas with Henry. This means it will have to go through multiple obstacles and possibly avoid collision with another vessel.', "If the vehicle is at the surface and has received a GPS update, it means that the vessel has successfully surfaced to provide new GPS coordinates to the command and control. This indicates that the vessel is ready to continue its mission.", 'At the moment, Alpha is moving towards point 2 while avoiding obstacle A to accomplish its objective and stay safe. Once, the vessel has reached its next waypoint, then it will start returning back for recovery.'];
    const options3_a = ['Gilda is about to move towards the left side of the map and loiter around using a new set of waypoints.', 'If Henry is at the surface and has received a GPS update, then it should be able to move towards the loiter area and continue its mission.', "Alpha is currently deployed to perform its objective, which is to move towards point 2 with a northwest heading and at a very fast speed. However, there is an obstacle named obstacle_a nearby in the southeast direction. Since the obstacle is not resolved and the proximity is close, alpha has activated the waypt_survey,avoid_obstacle_avoid_obstacle_a behavior to survey the area while avoiding the obstacle. This behavior allows alpha to continue towards its objective while ensuring safety and avoiding the obstacle."];
    const options1_b = ["Henry is in transit towards point 2 in the northwest, conducting a survey while consistently maintaining an approved depth range. As a result, the vessel is moving very fast under sea level but with a southwest heading as it turns around.", 'If Alpha no longer returns for pick up, it will circle around and start moving between the waypoints again.', 'The vessel needs a command by the operators to return back. At the moment, the vessel continues to fulfill its objectives while avoiding obstacles and other vessels.'];
    const options2_b = ['Henry is performing a survey and moving towards waypoint 2.', "If Alpha is no longer returning to its starting position, it would continue surveying the area without any intention of going back. There are no obstacles present and all previous obstacles have been resolved.", 'Gilda has not been instructed yet to return back, as a result, it continues to loiter while replanning its trajectory.'];
    const options3_b = ['Henry is moving under the water towards point 2 that is located northwest while surveying an area.', "If Alpha's return state is deactivated, then the vessel will continue surveying the area while also avoiding any present obstacles.", "If Gilda were to return instead of loitering while avoiding obstacles and vessels, it would need a command to return to its starting point. This alternative behavior would interrupt its current behavior of loitering and collision avoidance."];
    const queries_a = ['Please select the causal explanation that you think explains these events the best:', 'What if the vehicle is at the surface and has received a GPS update?', 'Why is alpha surveying the area while avoiding obstacle_a instead of returning to its starting point?'];
    const queries_b = ['Please select the causal explanation that you think explains these events the best:', 'What if Alpha is no longer returning to its starting position?', 'Why not Return instead of loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry?'];
    var images = [];
    var descriptions = [];
    var queries = [];
    var options1 = [];
    var options2 = [];
    var options3 = [];
    // Images
    var scenario1Image = scenario1Body.querySelector('.content img');
    var scenario2Image = scenario2Body.querySelector('.content img');
    var scenario3Image = scenario3Body.querySelector('.content img');
    // Descriptions
    var scenario1Description = scenario1Body.querySelector('.text p');
    var scenario2Description = scenario2Body.querySelector('.text p');
    var scenario3Description = scenario3Body.querySelector('.text p');
    // Queries
    var scenario1Query = scenario1Body.querySelector('.crowd-form-container p');
    var scenario2Query = scenario2Body.querySelector('.crowd-form-container p');
    var scenario3Query = scenario3Body.querySelector('.crowd-form-container p');
    // Options
    var scenario1Option1 = document.getElementById('scenario1Option1');
    var scenario1Option2 = document.getElementById('scenario1Option2');
    var scenario1Option3 = document.getElementById('scenario1Option3');
    var scenario1Option4 = document.getElementById('scenario1Option4');
    var scenario1Option5 = document.getElementById('scenario1Option5');
    var scenario2Option1 = document.getElementById('scenario2Option1');
    var scenario2Option2 = document.getElementById('scenario2Option2');
    var scenario2Option3 = document.getElementById('scenario2Option3');
    var scenario2Option4 = document.getElementById('scenario2Option4');
    var scenario2Option5 = document.getElementById('scenario2Option5');
    var scenario3Option1 = document.getElementById('scenario3Option1');
    var scenario3Option2 = document.getElementById('scenario3Option2');
    var scenario3Option3 = document.getElementById('scenario3Option3');
    var scenario3Option4 = document.getElementById('scenario3Option4');
    var scenario3Option5 = document.getElementById('scenario3Option5');
    var scenarioImage = null;
    var scenarioDescription = null;
    var scenarioQuery = null;
    var scenarioOption1 = null;
    var scenarioOption2 = null;
    var scenarioOption3 = null; 
    var answerButton = null;
    var sequence = 1;
    var qList = [];
    var selectedOption = null;
    const qHiddenInput = document.getElementById('questionHiddenInput');

    scenario1Option1.addEventListener('click', handleRadioClick);
    scenario1Option2.addEventListener('click', handleRadioClick);
    scenario1Option3.addEventListener('click', handleRadioClick);
    scenario1Option4.addEventListener('click', handleRadioClick);
    scenario1Option5.addEventListener('click', handleRadioClick);
    scenario2Option1.addEventListener('click', handleRadioClick);
    scenario2Option2.addEventListener('click', handleRadioClick);
    scenario2Option3.addEventListener('click', handleRadioClick);
    scenario2Option4.addEventListener('click', handleRadioClick);
    scenario2Option5.addEventListener('click', handleRadioClick);
    scenario3Option1.addEventListener('click', handleRadioClick);
    scenario3Option2.addEventListener('click', handleRadioClick);
    scenario3Option3.addEventListener('click', handleRadioClick);
    scenario3Option4.addEventListener('click', handleRadioClick);
    scenario3Option5.addEventListener('click', handleRadioClick);

    function handleRadioClick(event) {
        selectedOption = event.target.value;
        answerButton.disabled = false;
    }


    if (randomIndex === 0) {
        var series = 'a'
        images = images_a;
        descriptions = descriptions_a;
        queries = queries_a;
        options1 = options1_a;
        options2 = options2_a;
        options3 = options3_a;
    } else {
        var series = 'b'
        images = images_b;
        descriptions = descriptions_b;
        queries = queries_b;
        options1 = options1_b;
        options2 = options2_b;
        options3 = options3_b;
    }
    qList.push(series);
    // closingBody.hide();
    scenario2.hide();
    scenario3.hide();
    selectScenario();


    $('.collapse-text').text('(Click to collapse)');
    trigger.click(function () {
        content.toggle();
        var isVisible = content.is(':visible');
        if (isVisible) {
            $('.collapse-text').text('(Click to collapse)');
        } else {
            $('.collapse-text').text('(Click to expand)');
        }
    });

    answerButton1.addEventListener('click', function () {
        qList.push(selectedOption);
        selectScenario();
        scenario1.hide();
        scenario2.show();
        scenario2.focus();
    });

    answerButton2.addEventListener('click', function () {
        qList.push(selectedOption);
        selectScenario();
        scenario2.hide();
        scenario3.show();
        scenario3.focus();
    });

    answerButton3.addEventListener('click', function () {
        // scenario3.hide();
        // closingBody.show();
        // closingBody.focus();
        qList.push(selectedOption);
        qHiddenInput.value = qList;
    });

    function selectScenario() {
        condition = conditions.shift();
        qList.push(condition);
        focusOnBody();  
        console.log(condition);
        switch (condition) {
            case 1:
                scenarioImage.src = images[0];
                scenarioDescription.textContent = descriptions[0];
                scenarioQuery.textContent = queries[0];
                scenarioOption1.textContent = options1[0];
                scenarioOption2.textContent = options2[0];
                scenarioOption3.textContent = options3[0];
                scenarioOption1.value = options1[0];
                scenarioOption2.value = options2[0];
                scenarioOption3.value = options3[0];
                qList.push(queries[0]);
                break;
            case 2:
                scenarioImage.src = images[1];
                scenarioDescription.textContent = descriptions[1];
                scenarioQuery.textContent = queries[1];
                scenarioOption1.textContent = options1[1];
                scenarioOption2.textContent = options2[1];
                scenarioOption3.textContent = options3[1];
                scenarioOption1.value = options1[1];
                scenarioOption2.value = options2[1];
                scenarioOption3.value = options3[1];
                qList.push(queries[1]);
                break;
            case 3:
                scenarioImage.src = images[2];
                scenarioDescription.textContent = descriptions[2];
                scenarioQuery.textContent = queries[2];
                scenarioOption1.textContent = options1[2];
                scenarioOption2.textContent = options2[2];
                scenarioOption3.textContent = options3[2];
                scenarioOption1.value = options1[2];
                scenarioOption2.value = options2[2];
                scenarioOption3.value = options3[2];
                qList.push(queries[2]);
                break;
            default:
                console.log("Unknown scenario.");
        }

        return null;
    }

    function focusOnBody() {
        switch (sequence) {
            case 1:
                scenarioImage = scenario1Image;
                scenarioDescription = scenario1Description;
                scenarioQuery = scenario1Query;
                scenarioOption1 = scenario1Option1;
                scenarioOption2 = scenario1Option2;
                scenarioOption3 = scenario1Option3;
                answerButton = answerButton1;
                break;
            case 2:
                scenarioImage = scenario2Image;
                scenarioDescription = scenario2Description;
                scenarioQuery = scenario2Query;
                scenarioOption1 = scenario2Option1;
                scenarioOption2 = scenario2Option2;
                scenarioOption3 = scenario2Option3;
                answerButton = answerButton2;
                break;
            case 3:
                scenarioImage = scenario3Image;
                scenarioDescription = scenario3Description;
                scenarioQuery = scenario3Query;
                scenarioOption1 = scenario3Option1;
                scenarioOption2 = scenario3Option2;
                scenarioOption3 = scenario3Option3;
                answerButton = answerButton3;
                break;
            default:
                console.log("Unknown scenario.");
        }
        sequence++;
        return null;
    }
});

