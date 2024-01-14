import json
import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

streaming_history = Variable.get("streaming_history")
@dag(
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["spotify"],
)
def taskflow_api():
    @task()
    def extractTransform():
        order_data_dict = json.loads(streaming_history)
        return order_data_dict

    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        total_order_value = 0
        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}
    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        instead of saving it to end user review, just prints it out.
        """

        print(f"Total order value is: {total_order_value:.2f}")
    order_data = extractTransform()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])

taskflow_api()
