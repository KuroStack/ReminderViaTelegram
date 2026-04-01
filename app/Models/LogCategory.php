<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class LogCategory extends Model
{
    protected $fillable = ['name'];

    public function logs(): HasMany
    {
        return $this->hasMany(Log::class, 'category_id');
    }
}
