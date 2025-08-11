$(document).ready(function() {
    $('#fetchStoryBtn').click(function() {
        const storyId = $('#storyId').val().trim();
        if (!storyId) return alert('Please enter a JIRA Story ID');
        $.ajax({
            url: '/fetch_story',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ story_id: storyId }),
            success: function(res) {
                if (res.success) {
                    const story = res.story;
                    $('#storyIdDisplay').text(story.id);
                    $('#storySummary').text(story.summary);
                    $('#storyDescription').html(res.story.description);
                    $('#storyDetails').show();
                    // Generate test cases
                    $.ajax({
                        url: '/generate_tests',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({ story: story }),
                        success: function(res) {
                            if (res.success) {
                                const testCases = res.test_cases;
                                const tbody = $('#testCasesTable tbody');
                                tbody.empty();
                                testCases.forEach(tc => {
                                    tbody.append(`<tr><td>${tc.id}</td><td>${tc.description}</td></tr>`);
                                });
                                $('#testCasesSection').show();
                                $('#publishMsg').text('');
                            }
                        }
                    });
                } else {
                    alert('Failed to fetch story');
                }
            }
        });
    });

    $('#createZephyrBtn').click(function() {
        const storyId = $('#storyIdDisplay').text();
        const testCases = [];
        $('#testCasesTable tbody tr').each(function() {
            const id = $(this).find('td').eq(0).text();
            const description = $(this).find('td').eq(1).text();
            testCases.push({ id, description });
        });
        
        $('#zephyrMsg').text('Creating test cases in Zephyr Scale...').removeClass('text-success text-danger').addClass('text-info');
        $('#createdTestCases').empty(); // Clear previous results

        $.ajax({
            url: '/create_zephyr_tests_ui',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                story_key: storyId, 
                test_cases: testCases,
                project_id: 10000  // Default Zephyr project ID - you can make this configurable
            }),
            success: function(res) {
                if (res.success) {
                    $('#zephyrMsg').text(res.message).removeClass('text-info text-danger').addClass('text-success');
                    
                    if (res.created_keys && res.created_keys.length > 0) {
                        const list = $('<ul>').addClass('list-group mt-2');
                        res.created_keys.forEach(key => {
                            list.append($('<li>').addClass('list-group-item').text(key));
                        });
                        $('#createdTestCases').html('<strong>Created Test Cases:</strong>').append(list);
                    }

                } else {
                    $('#zephyrMsg').text(res.message || 'Failed to create test cases in Zephyr Scale').removeClass('text-info text-success').addClass('text-danger');
                }
            },
            error: function() {
                $('#zephyrMsg').text('Error connecting to Zephyr Scale').removeClass('text-info text-success').addClass('text-danger');
            }
        });
    });

    $('#publishBtn').click(function() {
        const storyId = $('#storyIdDisplay').text();
        const testCases = [];
        $('#testCasesTable tbody tr').each(function() {
            const id = $(this).find('td').eq(0).text();
            const description = $(this).find('td').eq(1).text();
            testCases.push({ id, description });
        });
        $.ajax({
            url: '/publish_tests',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ story_id: storyId, test_cases: testCases }),
            success: function(res) {
                if (res.success) {
                    $('#publishMsg').text(res.message).addClass('text-success');
                } else {
                    $('#publishMsg').text('Failed to publish test cases').addClass('text-danger');
                }
            }
        });
    });
}); 