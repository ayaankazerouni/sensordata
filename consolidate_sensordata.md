
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="#7799ee">
<td valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial">&nbsp;<br><big><big><strong>consolidate_sensordata</strong></big></big></font></td
><td align=right valign=bottom
><font color="#ffffff" face="helvetica, arial"><a href=".">index</a><br><a href="file:/home/ayaan/Developer/sensordata/consolidate_sensordata.py">/home/ayaan/Developer/sensordata/consolidate_sensordata.py</a></font></td></tr></table>
    <p><tt>Import&nbsp;and&nbsp;consolidate&nbsp;incremental&nbsp;development&nbsp;metrics&nbsp;from&nbsp;several&nbsp;sources.</tt></p>
<p>
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#aa55cc">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Modules</strong></big></font></td></tr>
    
<tr><td bgcolor="#aa55cc"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%"><table width="100%" summary="list"><tr><td width="25%" valign=top><a href="argparse.html">argparse</a><br>
</td><td width="25%" valign=top><a href="datetime.html">datetime</a><br>
</td><td width="25%" valign=top><a href="pandas.html">pandas</a><br>
</td><td width="25%" valign=top></td></tr></table></td></tr></table><p>
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#eeaa77">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Functions</strong></big></font></td></tr>
    
<tr><td bgcolor="#eeaa77"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%"><dl><dt><a name="-consolidate_student_data"><strong>consolidate_student_data</strong></a>(webcat_path=False, raw_inc_path=False, time_path=False, launch_totals_path=False)</dt><dd><tt>Import,&nbsp;format,&nbsp;and&nbsp;consolidate&nbsp;incremental&nbsp;development&nbsp;metrics&nbsp;from&nbsp;several&nbsp;sources.<br>
&nbsp;<br>
Keyword&nbsp;arguments:<br>
webcat_path&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;String&nbsp;path,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit<br>
raw_inc_path&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;String&nbsp;path,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit<br>
time_path&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;String&nbsp;path,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit<br>
ref_test_gains_path&nbsp;=&nbsp;String&nbsp;path,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit&nbsp;<br>
launch_totals_path&nbsp;&nbsp;=&nbsp;String&nbsp;path&nbsp;to&nbsp;work_session&nbsp;data,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit&nbsp;<br>
repo_mining_path&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;String&nbsp;path,&nbsp;None&nbsp;for&nbsp;default,&nbsp;or&nbsp;False&nbsp;to&nbsp;omit</tt></dd></dl>
 <dl><dt><a name="-load_final_score_data"><strong>load_final_score_data</strong></a>(webcat_path)</dt><dd><tt>Loads&nbsp;final&nbsp;score&nbsp;data&nbsp;from&nbsp;webcat_path.&nbsp;<br>
&nbsp;<br>
Only&nbsp;returns&nbsp;the&nbsp;student's&nbsp;final&nbsp;submission&nbsp;on&nbsp;each&nbsp;projects.&nbsp;<br>
Submission&nbsp;data&nbsp;is&nbsp;modified&nbsp;so&nbsp;that&nbsp;score.correctness&nbsp;only&nbsp;represents&nbsp;<br>
scores&nbsp;on&nbsp;instructor-written&nbsp;reference&nbsp;tests,&nbsp;and&nbsp;doesn't&nbsp;include&nbsp;points<br>
from&nbsp;students'&nbsp;own&nbsp;tests.</tt></dd></dl>
 <dl><dt><a name="-load_launch_totals"><strong>load_launch_totals</strong></a>(ws_path)</dt><dd><tt>Calculates&nbsp;and&nbsp;loads&nbsp;totals&nbsp;for&nbsp;Normal&nbsp;and&nbsp;Test&nbsp;launches.<br>
&nbsp;<br>
Operates&nbsp;on&nbsp;work&nbsp;session&nbsp;data.</tt></dd></dl>
 <dl><dt><a name="-load_launches"><strong>load_launches</strong></a>(sensordata_path)</dt><dd><tt>Loads&nbsp;raw&nbsp;launch&nbsp;data.<br>
&nbsp;<br>
Convenience&nbsp;method:&nbsp;filters&nbsp;out&nbsp;everything&nbsp;but&nbsp;Launches&nbsp;from&nbsp;raw&nbsp;sensordata.</tt></dd></dl>
 <dl><dt><a name="-load_raw_inc_data"><strong>load_raw_inc_data</strong></a>(raw_inc_path)</dt><dd><tt>Loads&nbsp;early/often&nbsp;metrics&nbsp;for&nbsp;code&nbsp;editing&nbsp;and&nbsp;launching.<br>
&nbsp;<br>
Note&nbsp;that&nbsp;this&nbsp;does&nbsp;NOT&nbsp;calculate&nbsp;the&nbsp;metrics.&nbsp;raw_inc_path&nbsp;refers<br>
to&nbsp;a&nbsp;CSV&nbsp;file&nbsp;that&nbsp;contains&nbsp;already-calculated&nbsp;values.</tt></dd></dl>
 <dl><dt><a name="-load_ref_test_data"><strong>load_ref_test_data</strong></a>(ref_test_gains_path)</dt><dd><tt>Loads&nbsp;reference&nbsp;test&nbsp;gain&nbsp;data.</tt></dd></dl>
 <dl><dt><a name="-load_time_spent_data"><strong>load_time_spent_data</strong></a>(time_path)</dt></dl>
</td></tr></table>
