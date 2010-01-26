<quiz>
	<title>Название теста</title>
	<content>Contents of quiz</content>
	<schema>scale</schema>
	<questions_per_page>1</questions_per_page>
	<result>
		<title>Title of first result</title>
		<content>Contents of result</content>
		<border>10</border>
	</result>
	<result>
		<title>Title of second result</title>
		<content>Contents of result</content>
		<border>20</border>
	</result>
	<question>
		<title>Title of first question</title>
		<content>Contents of question</content>
		<answer>
			<title>Title of first answer</title>
			<content>Contents of answer</content>
			<value>10</value>
			<depend>
				<result_title>Title of first result</result_title>
				<value>100</value>
			</depend>
		</answer>
		<answer>
			<title>Title of second answer</title>
			<content>Contents of answer</content>
			<value>20</value>
			<depend>
				<result_title>Title of second result</result_title>
				<value>100</value>
			</depend>
		</answer>
	</question>
	<question>
		<title>Title of second question</title>
		<content>Contents of question</content>
		<answer>
			<title>Title of first answer</title>
			<content>Contents of answer</content>
			<value>10</value>
			<depend>
				<result_title>Title of first result</result_title>
				<value>100</value>
			</depend>
		</answer>
		<answer>
			<title>Title of second answer</title>
			<content>Contents of answer</content>
			<value>20</value>
			<depend>
				<result_title>Title of second result</result_title>
				<value>100</value>
			</depend>
		</answer>
	</question>
</quiz>
