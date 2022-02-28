import numpy as np
class Incentive:

    def is_got_incentive(self, model, user, incentive_id):
        r = model.objects.filter(user_id=user.user_id, incentive_id=incentive_id)
        return len(r) == 1

    def insert_issued_incentive(self, model, issued_incentive):
        # print(issued_incentive)
        m = model(**issued_incentive)
        m.save()
        return True



