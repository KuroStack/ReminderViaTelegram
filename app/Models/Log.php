<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Log extends Model
{
    protected $fillable = ['category_id', 'subject', 'message', 'user_id'];

    public function category(): BelongsTo
    {
        return $this->belongsTo(LogCategory::class, 'category_id');
    }
}
