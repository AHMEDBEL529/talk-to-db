import aws_cdk as core
import aws_cdk.assertions as assertions

from talk_to_db.talk_to_db_stack import TalkToDbStack

# example tests. To run these tests, uncomment this file along with the example
# resource in talk_to_db/talk_to_db_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TalkToDbStack(app, "talk-to-db")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
