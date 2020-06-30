# mcqdb
<strong>Change the from and to date within the main.py file</strong> <span>Will be modified once .exe is made</span>
<hr>
<strong>Working steps</strong>
<ol>
  <li> Creates .metadata file if not present or the log files in Logs directory are modified </li>
  <li> .metadata contains start and end date of each log file </li>
  <li> left most file location of FROM DATE is found using .metadata using binary search</li>
  <li> Right most file location of TO DATE is found using .metadata using binary search</li>
  <li> left most insertion position is found for FROM DATE within file found using 3 step</li>
  <li> right most insertion position is found for TO DATE within file found using 4 step</li>
  <li> Results are printed </li>
</ol>
