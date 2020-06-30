# mcqdb
<h3>Usage</h3>
<ol>
    <li>Dist location contains executable file</li>
    <li><code>LogExtractor.exe -f</code> from date option</li>
    <li><code>LogExtractor.exe -t</code> to date option</li>
    <li><code>LogExtractor.exe -i</code> logs directory option</li>
    <li><code>LogExtractor.exe -o</code> output file option</li>
    <li>All the above options are mandatory</li>
    <li><code>LogExtractor.exe -h</code> help option</li>
</ol>
<h6>Example: </h6>
<code>LogExtractor.exe -f "1903-02-02T02:07:52Z" -t "1964-09-15T13:07:21Z" -i "logFiles" -o "output"</code>

<h3>Explanation</h3>
<ol>
   <li> The executable when run creates a .metadata file
      <ul>
          <li>Each row of .metadata file contains the first and last time-stamps of every log file this helps us locate in which files our from and to dates are present.</li>
          <li>A time-stamp is said to be present in a file if it exists between its last and first time-stamp. Using binary search these two file locations are found.</li>
          <li>When the programme is re-used .metadata file will not be re-created unless the log files are modified.</li>
      </ul>
  </li>
   <li>Next task would be to find in which specific row the from and to date is present within the file
    <ul>
          <li> Left most insertion position is found for fromDate within file-1 found from step 1.</li>
          <li> Right most insertion position is found for toDate within file-2 found from step 1.</li>
    </ul>
  </li>
   <li>Now we have all the information required for outputting our result.</li>
</ol>
<h3>Assumptions</h3>
<p>log files timestamps are in increasing order</p>
