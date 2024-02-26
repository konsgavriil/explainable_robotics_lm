import unittest
from semantic_accuracy import SemanticAccuracy

class TestAddFunction(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.sa = SemanticAccuracy()

    def test_random_input_random_output(self):
        input = "random input"
        output = "random output"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0)
        self.assertEqual(prec, 0)


    def test_good_input_random_output(self):
        input = "{'objective': 'Go to points 0, 1, 2, 3, 4, 5 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_b', 'obstacle_proximity': 'close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northeast', 'next_point_direction': 'northeast', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey,avoid_obstacle_avoid_obstacle_b'}"
        output = "random output"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0)
        self.assertEqual(prec, 0)

    def test_random_input_good_output(self):
        input = "random input"
        output = "Alpha is currently doing a survey and is approaching point 3. Despite the close proximity of obstacle B, the vehicle continues to move very fast towards its objective with a northeast heading, while also incorporating the behavior to avoid obstacle B."
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0)
        self.assertEqual(prec, 0)

    def test_good_input_subpar_output(self):
        input = "{'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_b', 'obstacle_proximity': 'close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point_3', 'speed': 'very fast', 'heading': 'northeast', 'next_point_direction': 'northeast', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey,avoid_obstacle_avoid_obstacle_b'}"
        output = "Gilda survey point 5."
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.5833333333333334)
        self.assertEqual(prec, 0.5)

    def test_subpar_input_good_output(self):
        input = "Gilda Henry survey loiter point 2 point 3 point "
        output = "Gilda loiter point 4."
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.9166666666666666)
        self.assertEqual(prec, 0.8333333333333334)

    def test_good_input_good_output(self):
        input = "{'objective': 'Go to points 0, 1, 2, 3, 4, 5 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_b', 'obstacle_proximity': 'close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northeast', 'next_point_direction': 'northeast', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey,avoid_obstacle_avoid_obstacle_b'}"
        output = "Alpha is currently doing a survey and is approaching point 3. Despite the close proximity of obstacle B, the vehicle continues to move very fast towards its objective with a northeast heading, while also incorporating the behavior to avoid obstacle B."
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.9901960784313726)
        self.assertEqual(prec, 0.9583333333333334)


    def test_good_cf_input_good_cf_output(self):
        input = "User query: What if the vehicle encounters an obstacle in close proximity while loitering?, Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avdcol_henry'}"  
        output = "Explanation: If the vehicle encounters an obstacle in close proximity while loitering, it will activate its collision avoidance behavior and adjust its trajectory to avoid the obstacle while continuing to loiter., State Permutation: 'obstacle_proximity': 'close'}"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 1.0)
        self.assertEqual(prec, 1.0)

    def test_random_cf_input_good_cf_output(self):
        input = "What if Dumbledore breaks the elder wand?"
        output = "Explanation: If the vehicle encounters an obstacle in close proximity while loitering, it will activate its collision avoidance behavior and adjust its trajectory to avoid the obstacle while continuing to loiter., State Permutation: 'obstacle_proximity': 'close'}"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.0)
        self.assertEqual(prec, 0.0)

    def test_good_cf_input_random_cf_output(self):
        input = "User query: What if the vehicle encounters an obstacle in close proximity while loitering?, Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avdcol_henry'}"  
        output = "If Dumbledore breaks the elder wand, then only two other Deathly Hallows will remain."
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.0)
        self.assertEqual(prec, 0.0)


    def test_good_cf_input_subpar_cf_output(self):
        input = "User query: What if the vehicle encounters an obstacle in close proximity while loitering?, Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point_7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avdcol_henry'}"  
        output = "point 7 obstacle 1 deploy"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.9333333333333332)
        self.assertEqual(prec, 0.9166666666666666)


    def test_good_cont_input_good_cont_output(self):
        input = "User query: Why is alpha surveying an area instead of returning to its starting point while avoiding obstacle C?, Representation: {'objective': 'Go to points 0, 1, 2, 3 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_c', 'obstacle_proximity': 'close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point1', 'speed': 'very fast', 'heading': 'southeast', 'next_point_direction': 'southeast', 'obstacle_direction': 'northeast', 'name': 'alpha', 'active_behaviour': 'waypt_survey'}"
        output = "Explanation: Alpha is currently deployed to perform its objective, specifically moving towards point 1 with a southeast heading and at a very fast speed. However, there is an obstacle named C in close proximity and it has not been resolved. This indicates that alpha should survey the area while avoiding obstacle C before returning to its starting point., State Permutation: Original: Waypt_survey,avoid_obstacle_avoid_obstacle_c\nModified: Waypt_return}"
        acc, prec = self.sa.compute(input, output)
        self.assertEqual(acc, 0.9937106918238993)
        self.assertEqual(prec, 0.9629629629629629)

    

if __name__ == '__main__':
    unittest.main()
